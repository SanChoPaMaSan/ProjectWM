#include "WMGameMode.h"

#include "EngineUtils.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerStart.h"
#include "LobbyPlayerController.h"
#include "StunDeliveryVehicle.h"
#include "TimerManager.h"
#include "UObject/UnrealType.h"

void AWMGameMode::BeginPlay()
{
    Super::BeginPlay();

    if (HasAuthority())
    {
        GetWorldTimerManager().SetTimer(
            MatchEndTimerHandle,
            this,
            &AWMGameMode::EndMatchByTimer,
            FMath::Max(1.0f, MatchDurationSeconds),
            false);
    }
}

void AWMGameMode::HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer)
{
    Super::HandleStartingNewPlayer_Implementation(NewPlayer);
    SpawnDeliveryVehicleFor(NewPlayer);
}

APawn* AWMGameMode::SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform& SpawnTransform)
{
    // HandleStartingNewPlayer runs Unreal's normal restart path first. WM has
    // its own HOUSE1/HOUSE2 spawn path below, so suppress the normal pawn to
    // prevent a second delivery vehicle from remaining near Player 2.
    return nullptr;
}

APlayerStart* AWMGameMode::FindHouseStart(FName HouseTag) const
{
    if (!GetWorld())
    {
        return nullptr;
    }

    for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It)
    {
        if (It->PlayerStartTag == HouseTag)
        {
            return *It;
        }
    }

    return nullptr;
}

void AWMGameMode::SpawnDeliveryVehicleFor(APlayerController* PlayerController)
{
    if (!PlayerController || !GetWorld() || !DefaultPawnClass)
    {
        UE_LOG(LogGameMode, Error, TEXT("WM spawn failed: invalid controller, world, or DefaultPawnClass."));
        return;
    }

    // The listen-server controller is Player 1/HOUSE1. The remote controller
    // is Player 2/HOUSE2. This works for PIE and for a LAN listen server.
    const FName HouseTag = PlayerController->IsLocalController() ? TEXT("HOUSE1") : TEXT("HOUSE2");
    APlayerStart* const Start = FindHouseStart(HouseTag);
    if (!Start)
    {
        UE_LOG(LogGameMode, Error, TEXT("WM spawn failed: no PlayerStart tagged %s."), *HouseTag.ToString());
        return;
    }

    if (APawn* ExistingPawn = PlayerController->GetPawn())
    {
        PlayerController->UnPossess();
        ExistingPawn->Destroy();
    }

    FActorSpawnParameters SpawnParams;
    SpawnParams.Owner = PlayerController;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    APawn* const DeliveryVehicle = GetWorld()->SpawnActor<APawn>(DefaultPawnClass, Start->GetActorTransform(), SpawnParams);
    if (!DeliveryVehicle)
    {
        UE_LOG(LogGameMode, Error, TEXT("WM spawn failed: could not create %s at %s."), *DefaultPawnClass->GetName(), *HouseTag.ToString());
        return;
    }

    const int32 PlayerIndex = PlayerController->IsLocalController() ? 1 : 2;
    if (AStunDeliveryVehicle* StunDeliveryVehicle = Cast<AStunDeliveryVehicle>(DeliveryVehicle))
    {
        StunDeliveryVehicle->SetTeamIndex(PlayerIndex);
    }
    PlayerController->Possess(DeliveryVehicle);
    PlayerController->SetControlRotation(Start->GetActorRotation());
    if (ALobbyPlayerController* LobbyController = Cast<ALobbyPlayerController>(PlayerController))
    {
        LobbyController->ClientAssignTeamIndex(PlayerIndex);
    }
    UE_LOG(LogGameMode, Log, TEXT("WM spawn success: %s -> %s (%s)"), *PlayerController->GetName(), *HouseTag.ToString(), *DeliveryVehicle->GetName());
}

void AWMGameMode::ReadHouseTrashCounts(int32& OutHouse1Count, int32& OutHouse2Count) const
{
    OutHouse1Count = 0;
    OutHouse2Count = 0;

    if (!GetWorld())
    {
        return;
    }

    for (TActorIterator<AActor> It(GetWorld()); It; ++It)
    {
        AActor* const Zone = *It;
        if (!Zone || !Zone->GetClass()->GetName().Contains(TEXT("BP_HouseTrashZone")))
        {
            continue;
        }

        const FIntProperty* HouseIdProperty = FindFProperty<FIntProperty>(Zone->GetClass(), TEXT("HouseID"));
        const FIntProperty* CountProperty = FindFProperty<FIntProperty>(Zone->GetClass(), TEXT("CurrentTrashCount"));
        if (!HouseIdProperty || !CountProperty)
        {
            UE_LOG(LogGameMode, Error, TEXT("WM match end could not read HouseID/CurrentTrashCount from %s."), *Zone->GetName());
            continue;
        }

        const int32 HouseId = HouseIdProperty->GetPropertyValue_InContainer(Zone);
        const int32 TrashCount = CountProperty->GetPropertyValue_InContainer(Zone);
        if (HouseId == 1)
        {
            OutHouse1Count = TrashCount;
        }
        else if (HouseId == 2)
        {
            OutHouse2Count = TrashCount;
        }
    }
}

void AWMGameMode::EndMatchByTimer()
{
    if (bMatchEnded || !GetWorld())
    {
        return;
    }

    bMatchEnded = true;
    int32 House1TrashCount = 0;
    int32 House2TrashCount = 0;
    ReadHouseTrashCounts(House1TrashCount, House2TrashCount);

    for (FConstPlayerControllerIterator It = GetWorld()->GetPlayerControllerIterator(); It; ++It)
    {
        ALobbyPlayerController* PlayerController = Cast<ALobbyPlayerController>(It->Get());
        if (!PlayerController)
        {
            continue;
        }

        PlayerController->SetIgnoreMoveInput(true);
        PlayerController->SetIgnoreLookInput(true);
        if (APawn* ControlledPawn = PlayerController->GetPawn())
        {
            ControlledPawn->DisableInput(PlayerController);
        }

        // HOUSE1 scores the trash currently inside HOUSE2, and HOUSE2 scores
        // the trash currently inside HOUSE1.
        const bool bHouse1Player = PlayerController->IsLocalController();
        const int32 OurScore = bHouse1Player ? House2TrashCount : House1TrashCount;
        const int32 OpponentScore = bHouse1Player ? House1TrashCount : House2TrashCount;
        PlayerController->ClientShowMatchResult(OurScore, OpponentScore);
    }
}
