#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TrafficStartActor.generated.h"

class ATrafficCarActor;
class UArrowComponent;

/** Base for BP_RoadPathStart. Spawns one random configured car every 5-10 seconds. */
UCLASS()
class PROJECTWM_API ATrafficStartActor : public AActor
{
    GENERATED_BODY()

public:
    ATrafficStartActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Traffic")
    TObjectPtr<UArrowComponent> DirectionArrow;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Traffic")
    TArray<TSubclassOf<ATrafficCarActor>> CarClasses;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Traffic", meta = (ClampMin = "0.1"))
    float MinSpawnInterval = 5.0f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Traffic", meta = (ClampMin = "0.1"))
    float MaxSpawnInterval = 10.0f;

private:
    void SpawnRandomCar();
    void ScheduleNextSpawn();
    FTimerHandle SpawnTimerHandle;
};
