#include "StunTrashActor.h"

#include "StunDeliveryVehicle.h"
#include "TimerManager.h"

AStunTrashActor::AStunTrashActor()
{
    bReplicates = true;
    SetReplicateMovement(true);
}

void AStunTrashActor::NotifyActorBeginOverlap(AActor* OtherActor)
{
    Super::NotifyActorBeginOverlap(OtherActor);

    // Physics and collision are authoritative on the server.  A held trash item
    // remains attached to a vehicle, so it cannot stun its carrier while stored.
    if (!HasAuthority() || !bCanStun || IsHidden() || GetAttachParentActor())
    {
        return;
    }

    AStunDeliveryVehicle* DeliveryVehicle = Cast<AStunDeliveryVehicle>(OtherActor);
    if (!DeliveryVehicle || !DeliveryVehicle->ApplyTrash4Stun(5.0f))
    {
        return;
    }

    bCanStun = false;
    GetWorldTimerManager().SetTimer(RearmTimerHandle, this, &AStunTrashActor::RearmStun, 5.0f, false);
}

void AStunTrashActor::RearmStun()
{
    bCanStun = true;
}
