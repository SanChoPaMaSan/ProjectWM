#include "SlowZoneArea.h"

#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "StunDeliveryVehicle.h"
#include "UObject/ConstructorHelpers.h"

ASlowZoneArea::ASlowZoneArea()
{
    bReplicates = true;
    SetReplicateMovement(true);
    InitialLifeSpan = 3.0f;

    SlowRadius = CreateDefaultSubobject<USphereComponent>(TEXT("SlowRadius"));
    SlowRadius->InitSphereRadius(320.0f);
    SlowRadius->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    SlowRadius->SetCollisionResponseToAllChannels(ECR_Ignore);
    SlowRadius->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
    SetRootComponent(SlowRadius);
    SlowRadius->OnComponentBeginOverlap.AddDynamic(this, &ASlowZoneArea::HandleOverlap);

    UStaticMeshComponent* const Visual = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("SlowZoneVisual"));
    Visual->SetupAttachment(SlowRadius);
    Visual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Visual->SetCastShadow(false);
    // The owner is placed slightly outside the hit surface, so keep the disc centered
    // instead of embedding it in floors and causing depth flicker.
    Visual->SetRelativeLocation(FVector::ZeroVector);
    Visual->SetRelativeScale3D(FVector(6.4f, 6.4f, 0.08f));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    if (CylinderMesh.Succeeded())
    {
        Visual->SetStaticMesh(CylinderMesh.Object);
    }
}

void ASlowZoneArea::HandleOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
    UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
    if (HasAuthority())
    {
        if (AStunDeliveryVehicle* const Vehicle = Cast<AStunDeliveryVehicle>(OtherActor))
        {
            Vehicle->ApplyTrash2Slow(3.0f);
        }
    }
}
