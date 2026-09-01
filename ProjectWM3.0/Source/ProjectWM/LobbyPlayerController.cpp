#include "LobbyPlayerController.h"

#include "Blueprint/UserWidget.h"
#include "Blueprint/WidgetTree.h"
#include "Components/TextBlock.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/StructOnScope.h"
#include "UObject/UObjectIterator.h"
#include "UObject/UnrealType.h"
#include "GameFramework/GameModeBase.h"
#include "GameResultWidget.h"
#include "LobbyMenuWidget.h"
#include "TimerManager.h"

namespace
{
bool CallScoreTextFunction(UUserWidget* Widget, FName FunctionName, FText& OutText)
{
    UFunction* const Function = Widget ? Widget->FindFunction(FunctionName) : nullptr;
    if (!Function || !Function->GetReturnProperty())
    {
        return false;
    }

    const FTextProperty* const ReturnProperty = CastField<FTextProperty>(Function->GetReturnProperty());
    if (!ReturnProperty)
    {
        return false;
    }

    FStructOnScope Parameters(Function);
    Widget->ProcessEvent(Function, Parameters.GetStructMemory());
    OutText = ReturnProperty->GetPropertyValue_InContainer(Parameters.GetStructMemory());
    return true;
}

bool ExtractTrailingScore(const FText& ScoreText, int32& OutScore)
{
    const FString Source = ScoreText.ToString().TrimStartAndEnd();
    int32 End = Source.Len() - 1;
    while (End >= 0 && !FChar::IsDigit(Source[End]))
    {
        --End;
    }

    if (End < 0)
    {
        return false;
    }

    int32 Start = End;
    while (Start > 0 && FChar::IsDigit(Source[Start - 1]))
    {
        --Start;
    }

    OutScore = FCString::Atoi(*Source.Mid(Start, End - Start + 1));
    return true;
}
}

ALobbyPlayerController::ALobbyPlayerController()
{
    static ConstructorHelpers::FClassFinder<ULobbyMenuWidget> LobbyMenuFinder(
        TEXT("/Game/UI/WBP_LobbyMenu"));

    if (LobbyMenuFinder.Succeeded())
    {
        LobbyMenuClass = LobbyMenuFinder.Class;
    }
}

void ALobbyPlayerController::BeginPlay()
{
    Super::BeginPlay();

    // The server owns remote PlayerControllers too. Only a local controller
    // may create viewport UI; otherwise CreateWidget/AddToViewport is None.
    if (!IsLocalController())
    {
        return;
    }

    // This controller is also used as WM's seamless-travel replacement
    // controller. The lobby widget must only ever be created in LV_Lobby.
    if (!GetWorld() || !GetWorld()->GetMapName().Contains(TEXT("LV_Lobby")))
    {
        ConfigureForCurrentMap();
        return;
    }

    if (!LobbyMenuClass)
    {
        return;
    }

    LobbyWidget = CreateWidget<ULobbyMenuWidget>(this, LobbyMenuClass);
    if (!LobbyWidget)
    {
        return;
    }

    LobbyWidget->AddToViewport();
    FInputModeUIOnly InputMode;
    InputMode.SetWidgetToFocus(LobbyWidget->TakeWidget());
    SetInputMode(InputMode);
    bShowMouseCursor = true;
}

void ALobbyPlayerController::BeginPlayingState()
{
    Super::BeginPlayingState();
    ConfigureForCurrentMap();
}

void ALobbyPlayerController::PostSeamlessTravel()
{
    Super::PostSeamlessTravel();
    ConfigureForCurrentMap();

    // The Lobby controller is intentionally carried across seamless travel in
    // PIE. Remove any lobby pawn and let WM's GameMode create and possess its
    // configured BP_DeliveryVehicle_v1 pawn for every player.
    if (HasAuthority() && GetWorld() && !GetWorld()->GetMapName().Contains(TEXT("LV_Lobby")))
    {
        if (APawn* ExistingPawn = GetPawn())
        {
            ExistingPawn->Destroy();
        }

        if (AGameModeBase* GameMode = GetWorld()->GetAuthGameMode())
        {
            GameMode->RestartPlayer(this);
        }
    }
}

void ALobbyPlayerController::ConfigureForCurrentMap()
{
    if (!IsLocalController() || !GetWorld())
    {
        return;
    }

    // PlayerControllers persist through seamless travel. The lobby's UI-only
    // input mode must not carry into WM, or the spawned delivery vehicle
    // cannot receive movement input.
    const FString MapName = GetWorld()->GetMapName();
    if (!MapName.Contains(TEXT("LV_Lobby")))
    {
        if (LobbyWidget)
        {
            LobbyWidget->RemoveFromParent();
            LobbyWidget = nullptr;
        }

        SetInputMode(FInputModeGameOnly());
        bShowMouseCursor = false;
    }
}

void ALobbyPlayerController::ClientShowMatchResult_Implementation(int32 OurScore, int32 OpponentScore)
{
    if (!IsLocalController() || GameResultWidget)
    {
        return;
    }

    SetIgnoreMoveInput(true);
    SetIgnoreLookInput(true);
    if (APawn* ControlledPawn = GetPawn())
    {
        ControlledPawn->DisableInput(this);
    }

    GameResultWidget = CreateWidget<UGameResultWidget>(this, UGameResultWidget::StaticClass());
    if (!GameResultWidget)
    {
        return;
    }

    GameResultWidget->SetResult(OurScore, OpponentScore);
    GameResultWidget->AddToViewport(1000);

    FInputModeUIOnly InputMode;
    InputMode.SetWidgetToFocus(GameResultWidget->TakeWidget());
    SetInputMode(InputMode);
    bShowMouseCursor = true;
}

void ALobbyPlayerController::ClientAssignTeamIndex_Implementation(int32 TeamIndex)
{
    PendingTeamIndex = TeamIndex;
    TeamIndexApplyAttempts = 0;
    ApplyPendingTeamIndex();

    if (GetWorld() && !GetWorldTimerManager().IsTimerActive(TeamIndexApplyTimerHandle))
    {
        GetWorldTimerManager().SetTimer(
            TeamIndexApplyTimerHandle,
            this,
            &ALobbyPlayerController::ApplyPendingTeamIndex,
            0.25f,
            true);
    }
}

void ALobbyPlayerController::ApplyPendingTeamIndex()
{
    if (!IsLocalController() || PendingTeamIndex <= 0 || !GetWorld())
    {
        return;
    }

    for (TObjectIterator<UUserWidget> It; It; ++It)
    {
        UUserWidget* const Widget = *It;
        if (!Widget || Widget->GetWorld() != GetWorld() || !Widget->GetClass()->GetName().Contains(TEXT("WBP_RobotHUD")))
        {
            continue;
        }

        FText BaseOurText;
        FText BaseOpponentText;
        int32 BaseOurScore = 0;
        int32 BaseOpponentScore = 0;
        if (!CallScoreTextFunction(Widget, TEXT("GetOurTeamScoreText"), BaseOurText)
            || !CallScoreTextFunction(Widget, TEXT("GetOpponentTeamScoreText"), BaseOpponentText)
            || !ExtractTrailingScore(BaseOurText, BaseOurScore)
            || !ExtractTrailingScore(BaseOpponentText, BaseOpponentScore))
        {
            continue;
        }

        const int32 OurScore = PendingTeamIndex == 2 ? BaseOpponentScore : BaseOurScore;
        const int32 OpponentScore = PendingTeamIndex == 2 ? BaseOurScore : BaseOpponentScore;

        TArray<UWidget*> AllWidgets;
        Widget->WidgetTree->GetAllWidgets(AllWidgets);
        for (UWidget* Child : AllWidgets)
        {
            UTextBlock* const TextBlock = Cast<UTextBlock>(Child);
            if (!TextBlock)
            {
                continue;
            }

            const FString ExistingText = TextBlock->GetText().ToString();
            if (ExistingText.Contains(TEXT("우리팀 점수")))
            {
                TextBlock->SetText(FText::FromString(FString::Printf(TEXT("우리팀 점수 : %d"), OurScore)));
            }
            else if (ExistingText.Contains(TEXT("상대팀 점수")))
            {
                TextBlock->SetText(FText::FromString(FString::Printf(TEXT("상대팀 점수 : %d"), OpponentScore)));
            }
        }
    }

    ++TeamIndexApplyAttempts;
    if (GameResultWidget || TeamIndexApplyAttempts >= 7200)
    {
        GetWorldTimerManager().ClearTimer(TeamIndexApplyTimerHandle);
    }
}
