#include "TrashSlowZoneActor.h"

#include "SlowZoneArea.h"
#include "Engine/World.h"
#include "Math/RotationMatrix.h"

ATrashSlowZoneActor::ATrashSlowZoneActor()
{
    bReplicates = true;
    SetReplicateMovement(true);
}

void ATrashSlowZoneActor::ArmSlowZoneForThrow()
{
    if (HasAuthority())
    {
        bSlowZoneArmed = true;
    }
}

void ATrashSlowZoneActor::NotifyHit(UPrimitiveComponent* MyComp, AActor* Other, UPrimitiveComponent* OtherComp,
    bool bSelfMoved, FVector HitLocation, FVector HitNormal, FVector NormalImpulse, const FHitResult& Hit)
{
    Super::NotifyHit(MyComp, Other, OtherComp, bSelfMoved, HitLocation, HitNormal, NormalImpulse, Hit);

    if (!HasAuthority() || !bSlowZoneArmed || IsHidden() || GetAttachParentActor())
    {
        return;
    }

    const float CurrentTime = GetWorld()->GetTimeSeconds();
    if (CurrentTime < NextZoneSpawnTime)
    {
        return;
    }

    ActiveZones.RemoveAll([](const TWeakObjectPtr<ASlowZoneArea>& Zone)
    {
        return !IsValid(Zone.Get());
    });
    while (ActiveZones.Num() >= MaxActiveZones)
    {
        if (ASlowZoneArea* const OldestZone = ActiveZones[0].Get())
        {
            OldestZone->Destroy();
        }
        ActiveZones.RemoveAt(0);
    }

    const FVector SurfaceNormal = Hit.ImpactNormal.IsNearlyZero() ? FVector::UpVector : Hit.ImpactNormal.GetSafeNormal();
    const FVector ZoneLocation = Hit.ImpactPoint + SurfaceNormal * ZoneSurfaceOffset;
    const FRotator ZoneRotation = FRotationMatrix::MakeFromZ(SurfaceNormal).Rotator();
    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
    if (ASlowZoneArea* const NewZone = GetWorld()->SpawnActor<ASlowZoneArea>(
        ASlowZoneArea::StaticClass(), ZoneLocation, ZoneRotation, SpawnParams))
    {
        ActiveZones.Add(NewZone);
        NextZoneSpawnTime = CurrentTime + ZoneSpawnCooldownSeconds;
    }
}
