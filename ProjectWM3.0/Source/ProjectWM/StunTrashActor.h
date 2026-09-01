#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "StunTrashActor.generated.h"

/** Base used by BP_Trash4. A single trash item rearms five seconds after a successful stun. */
UCLASS()
class PROJECTWM_API AStunTrashActor : public AActor
{
    GENERATED_BODY()

public:
    AStunTrashActor();

    virtual void NotifyActorBeginOverlap(AActor* OtherActor) override;

private:
    void RearmStun();

    /** Server-only cooldown; attached/hidden trash is never allowed to stun. */
    bool bCanStun = true;
    FTimerHandle RearmTimerHandle;
};
