#include "TrafficCarActor.h"

#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"

ATrafficCarActor::ATrafficCarActor()
{
    bReplicates = true;
    SetReplicateMovement(true);
    PrimaryActorTick.bCanEverTick = true;

    TrafficRoot = CreateDefaultSubobject<USceneComponent>(TEXT("TrafficRoot"));
    SetRootComponent(TrafficRoot);
    CarMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CarMesh"));
    CarMesh->SetupAttachment(TrafficRoot);
    CarMesh->SetMobility(EComponentMobility::Movable);
    CarMesh->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    CarMesh->SetCollisionResponseToAllChannels(ECR_Ignore);
    CarMesh->SetCollisionResponseToChannel(ECC_WorldDynamic, ECR_Overlap);
    CarMesh->SetGenerateOverlapEvents(true);
    // Imported cars use local -Y as their nose. Rotate the visual so it faces
    // the StartBP arrow / actor travel direction (+X), rather than reversing it.
    CarMesh->SetRelativeRotation(FRotator(0.0f, 90.0f, 0.0f));
}

void ATrafficCarActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (HasAuthority() && MoveSpeed > 0.0f)
    {
        AddActorWorldOffset(GetActorForwardVector() * MoveSpeed * DeltaSeconds, false);
    }
}
