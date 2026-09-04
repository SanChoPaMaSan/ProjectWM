#include "TrashKnockbackActor.h"

#include "StunDeliveryVehicle.h"
#include "TimerManager.h"

ATrashKnockbackActor::ATrashKnockbackActor()
{
    bReplicates = true;
    SetReplicateMovement(true);
}

void ATrashKnockbackActor::NotifyActorBeginOverlap(AActor* OtherActor)
{
    Super::NotifyActorBeginOverlap(OtherActor);
    TryApplyKnockback(OtherActor);
}

void ATrashKnockbackActor::NotifyHit(UPrimitiveComponent* MyComp, AActor* Other, UPrimitiveComponent* OtherComp,
    bool bSelfMoved, FVector HitLocation, FVector HitNormal, FVector NormalImpulse, const FHitResult& Hit)
{
    Super::NotifyHit(MyComp, Other, OtherComp, bSelfMoved, HitLocation, HitNormal, NormalImpulse, Hit);
    TryApplyKnockback(Other);
}

void ATrashKnockbackActor::TryApplyKnockback(AActor* OtherActor)
{
    if (!HasAuthority() || !bCanKnockback || IsHidden() || GetAttachParentActor())
    {
        return;
    }

    AStunDeliveryVehicle* const Vehicle = Cast<AStunDeliveryVehicle>(OtherActor);
    if (!Vehicle)
    {
        return;
    }

    FVector Direction = Vehicle->GetActorLocation() - GetActorLocation();
    Direction.Z = 0.0f;
    Vehicle->ApplyTrash1Knockback(Direction.GetSafeNormal(), 800.0f);

    bCanKnockback = false;
    GetWorldTimerManager().SetTimer(KnockbackCooldownHandle, this, &ATrashKnockbackActor::RearmKnockback, 1.0f, false);
}

void ATrashKnockbackActor::RearmKnockback()
{
    bCanKnockback = true;
}
