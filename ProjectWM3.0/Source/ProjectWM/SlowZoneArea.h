#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SlowZoneArea.generated.h"

class USphereComponent;

/** Replicated three-second area created by Trash2. */
UCLASS()
class PROJECTWM_API ASlowZoneArea : public AActor
{
    GENERATED_BODY()

public:
    ASlowZoneArea();

protected:
    UFUNCTION()
    void HandleOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
        UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USphereComponent> SlowRadius;
};
