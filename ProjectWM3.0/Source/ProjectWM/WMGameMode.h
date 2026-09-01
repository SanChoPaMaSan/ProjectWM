#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "WMGameMode.generated.h"

class APlayerStart;

UCLASS()
class PROJECTWM_API AWMGameMode : public AGameModeBase
{
    GENERATED_BODY()

protected:
    virtual void BeginPlay() override;
    virtual void HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer) override;
    virtual APawn* SpawnDefaultPawnAtTransform_Implementation(AController* NewPlayer, const FTransform& SpawnTransform) override;

    UPROPERTY(EditDefaultsOnly, Category = "Match")
    float MatchDurationSeconds = 180.0f;

private:
    APlayerStart* FindHouseStart(FName HouseTag) const;
    void SpawnDeliveryVehicleFor(APlayerController* PlayerController);
    void EndMatchByTimer();
    void ReadHouseTrashCounts(int32& OutHouse1Count, int32& OutHouse2Count) const;

    FTimerHandle MatchEndTimerHandle;
    bool bMatchEnded = false;
};
