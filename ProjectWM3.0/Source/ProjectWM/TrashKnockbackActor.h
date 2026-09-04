#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TrashKnockbackActor.generated.h"

/** Base for BP_Trash1: a thrown item pushes a delivery vehicle away on impact. */
UCLASS()
class PROJECTWM_API ATrashKnockbackActor : public AActor
{
    GENERATED_BODY()

public:
    ATrashKnockbackActor();
    virtual void NotifyActorBeginOverlap(AActor* OtherActor) override;
    virtual void NotifyHit(UPrimitiveComponent* MyComp, AActor* Other, UPrimitiveComponent* OtherComp,
        bool bSelfMoved, FVector HitLocation, FVector HitNormal, FVector NormalImpulse, const FHitResult& Hit) override;

private:
    void TryApplyKnockback(AActor* OtherActor);
    void RearmKnockback();

    bool bCanKnockback = true;
    FTimerHandle KnockbackCooldownHandle;
};
