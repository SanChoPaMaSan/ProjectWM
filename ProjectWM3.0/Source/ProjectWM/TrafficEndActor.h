#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TrafficEndActor.generated.h"

class UBoxComponent;

/** Base for BP_RoadPathEnd. Removes traffic cars that enter the end volume. */
UCLASS()
class PROJECTWM_API ATrafficEndActor : public AActor
{
    GENERATED_BODY()

public:
    ATrafficEndActor();

    virtual void Tick(float DeltaSeconds) override;

private:
    void DespawnTraffic(AActor* OtherActor);

    UFUNCTION()
    void HandleTrafficOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep,
        const FHitResult& SweepResult);

    UPROPERTY(VisibleAnywhere, Category = "Traffic")
    TObjectPtr<UBoxComponent> EndTrigger;
};
