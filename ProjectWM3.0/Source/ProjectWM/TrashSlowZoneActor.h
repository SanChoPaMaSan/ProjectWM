#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TrashSlowZoneActor.generated.h"

/** Base for BP_Trash2: the first physical impact creates a temporary slow zone. */
UCLASS()
class PROJECTWM_API ATrashSlowZoneActor : public AActor
{
    GENERATED_BODY()

public:
    ATrashSlowZoneActor();

    /** Enables the one-shot slow-zone impact only after this trash is thrown by a player. */
    void ArmSlowZoneForThrow();

    virtual void NotifyHit(UPrimitiveComponent* MyComp, AActor* Other, UPrimitiveComponent* OtherComp,
        bool bSelfMoved, FVector HitLocation, FVector HitNormal, FVector NormalImpulse, const FHitResult& Hit) override;

private:
    // Floor contact at map spawn must not consume the trash or create a zone.
    bool bSlowZoneArmed = false;

    // A bouncing trash can report several physics contacts in one frame.
    float NextZoneSpawnTime = 0.0f;
    TArray<TWeakObjectPtr<class ASlowZoneArea>> ActiveZones;

    static constexpr float ZoneSpawnCooldownSeconds = 0.18f;
    static constexpr int32 MaxActiveZones = 8;
    static constexpr float ZoneSurfaceOffset = 4.0f;
};
