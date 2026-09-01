#include "LobbyMenuWidget.h"

#include "Components/Button.h"
#include "Components/EditableTextBox.h"
#include "Components/TextBlock.h"
#include "Engine/GameInstance.h"
#include "GameFramework/GameStateBase.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"

void ULobbyMenuWidget::NativeConstruct()
{
    Super::NativeConstruct();

    // Remove legacy Blueprint button handlers. They used OpenLevel on every
    // local window, which could rebuild the server and disconnect Player2.
    if (HostButton)
    {
        HostButton->OnClicked.Clear();
        HostButton->OnClicked.AddDynamic(this, &ULobbyMenuWidget::CreateRoom);
    }
    if (JoinButton)
    {
        JoinButton->OnClicked.Clear();
        JoinButton->OnClicked.AddDynamic(this, &ULobbyMenuWidget::JoinRoom);
    }
    if (StartButton)
    {
        StartButton->OnClicked.Clear();
        StartButton->OnClicked.AddDynamic(this, &ULobbyMenuWidget::StartMatch);
    }

    RefreshLobbyState();
}

void ULobbyMenuWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
    Super::NativeTick(MyGeometry, InDeltaTime);
    RefreshLobbyState();
}

bool ULobbyMenuWidget::IsListenServer() const
{
    return GetWorld() && GetWorld()->GetNetMode() == NM_ListenServer;
}

bool ULobbyMenuWidget::HasTwoPlayers() const
{
    const UWorld* World = GetWorld();
    const AGameStateBase* GameState = World ? World->GetGameState() : nullptr;
    return GameState && GameState->PlayerArray.Num() >= 2;
}

void ULobbyMenuWidget::SetStatus(const FText& Text) const
{
    if (LobbyStatus)
    {
        LobbyStatus->SetText(Text);
    }
}

void ULobbyMenuWidget::RefreshLobbyState()
{
    const bool bHost = IsListenServer();
    const bool bReady = bHost && HasTwoPlayers();

    if (HostButton)
    {
        HostButton->SetIsEnabled(!bHost);
    }
    if (JoinButton)
    {
        JoinButton->SetIsEnabled(!bHost);
    }
    if (StartButton)
    {
        StartButton->SetIsEnabled(bReady);
    }

    if (bHost)
    {
        SetStatus(bReady
            ? FText::FromString(TEXT("2명 참가 완료 - Host가 게임을 시작할 수 있습니다."))
            : FText::FromString(TEXT("방 생성됨 - 참가자를 기다리는 중입니다.")));
    }
    else if (GetWorld() && GetWorld()->GetNetMode() == NM_Client)
    {
        SetStatus(FText::FromString(TEXT("방에 참가했습니다. Host의 게임 시작을 기다리는 중입니다.")));
    }
    else
    {
        SetStatus(FText::FromString(TEXT("방을 만들거나 서버 IP를 입력해 접속하세요.")));
    }
}

void ULobbyMenuWidget::CreateRoom()
{
    if (IsListenServer())
    {
        SetStatus(FText::FromString(TEXT("이미 방이 열려 있습니다.")));
        return;
    }

    if (GetWorld() && GetWorld()->GetNetMode() == NM_Client)
    {
        SetStatus(FText::FromString(TEXT("참가자는 방을 만들 수 없습니다.")));
        return;
    }

    UGameplayStatics::OpenLevel(this, FName(TEXT("LV_Lobby")), true, TEXT("listen"));
}

void ULobbyMenuWidget::JoinRoom()
{
    if (IsListenServer())
    {
        SetStatus(FText::FromString(TEXT("Host는 참가하기를 사용할 수 없습니다.")));
        return;
    }

    const FString Address = ServerIPInput ? ServerIPInput->GetText().ToString().TrimStartAndEnd() : FString();
    if (Address.IsEmpty())
    {
        SetStatus(FText::FromString(TEXT("서버 IP:포트를 입력하세요. 예: 192.168.0.15:7777")));
        return;
    }

    if (APlayerController* Controller = GetOwningPlayer())
    {
        Controller->ClientTravel(Address, TRAVEL_Absolute);
    }
}

void ULobbyMenuWidget::StartMatch()
{
    if (!IsListenServer() || !HasTwoPlayers())
    {
        return;
    }

    // This world is already the listen server created by CreateRoom.  Adding
    // ?listen again is unnecessary and can make packaged travel fall back to
    // the default map if the destination is not resolved cleanly.
    GetWorld()->ServerTravel(TEXT("/Game/LEVEL/WM"), true);
}
