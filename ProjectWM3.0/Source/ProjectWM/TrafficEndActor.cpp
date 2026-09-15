#include "TrafficEndActor.h"

#include "Components/BoxComponent.h"
#include "EngineUtils.h"
#include "TrafficCarActor.h"

ATrafficEndActor::ATrafficEndActor()
{
    bReplicates = true;
    PrimaryActorTick.bCanEverTick = true;
    EndTrigger = CreateDefaultSubobject<UBoxComponent>(TEXT("EndTrigger"));
    SetRootComponent(EndTrigger);
    // WM lanes are 600 cm apart (Y=+/-300). Keep the trigger on its own lane.
    EndTrigger->SetBoxExtent(FVector(300.0f, 150.0f, 300.0f));
    EndTrigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    EndTrigger->SetCollisionResponseToAllChannels(ECR_Ignore);
    EndTrigger->SetCollisionResponseToChannel(ECC_WorldDynamic, ECR_Overlap);
    EndTrigger->SetGenerateOverlapEvents(true);
    EndTrigger->OnComponentBeginOverlap.AddDynamic(this, &ATrafficEndActor::HandleTrafficOverlap);
}

void ATrafficEndActor::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!HasAuthority())
    {
        return;
    }

    // Imported FBX collision can vary per car. Keep the overlap event above, but
    // also remove a car once its actor origin reaches this endpoint reliably.
    for (TActorIterator<ATrafficCarActor> It(GetWorld()); It; ++It)
    {
        if (FVector::DistSquared(It->GetActorLocation(), GetActorLocation()) <= FMath::Square(350.0f))
        {
            DespawnTraffic(*It);
        }
    }
}

void ATrafficEndActor::HandleTrafficOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
    UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
    if (HasAuthority() && Cast<ATrafficCarActor>(OtherActor))
    {
        DespawnTraffic(OtherActor);
    }
}

void ATrafficEndActor::DespawnTraffic(AActor* OtherActor)
{
    if (!IsValid(OtherActor) || !Cast<ATrafficCarActor>(OtherActor))
    {
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Traffic despawn: %s at %s location=%s"),
        *OtherActor->GetName(), *GetName(), *OtherActor->GetActorLocation().ToString());
    OtherActor->Destroy();
}
