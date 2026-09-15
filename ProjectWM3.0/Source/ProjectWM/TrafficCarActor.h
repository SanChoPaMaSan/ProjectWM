#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TrafficCarActor.generated.h"

class UStaticMeshComponent;
class USceneComponent;

/** Base for BP_Car1~7. Moves forward at a fixed speed from the Start arrow. */
UCLASS(Abstract)
class PROJECTWM_API ATrafficCarActor : public AActor
{
    GENERATED_BODY()

public:
    ATrafficCarActor();
    virtual void Tick(float DeltaSeconds) override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Traffic")
    TObjectPtr<USceneComponent> TrafficRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Traffic")
    TObjectPtr<UStaticMeshComponent> CarMesh;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Traffic", meta = (ClampMin = "0.0"))
    float MoveSpeed = 900.0f;
};
