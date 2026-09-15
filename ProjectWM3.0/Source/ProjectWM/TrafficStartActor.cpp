#include "TrafficStartActor.h"

#include "Components/ArrowComponent.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "TrafficCarActor.h"

ATrafficStartActor::ATrafficStartActor()
{
    bReplicates = true;
    DirectionArrow = CreateDefaultSubobject<UArrowComponent>(TEXT("DirectionArrow"));
    SetRootComponent(DirectionArrow);
    DirectionArrow->ArrowColor = FColor(80, 210, 255);
    DirectionArrow->ArrowSize = 2.0f;
}

void ATrafficStartActor::BeginPlay()
{
    Super::BeginPlay();
    if (HasAuthority())
    {
        // WM begins with traffic already on both lanes; each later spawn is randomized.
        SpawnRandomCar();
    }
}

void ATrafficStartActor::ScheduleNextSpawn()
{
    const float MinDelay = FMath::Max(0.1f, MinSpawnInterval);
    const float MaxDelay = FMath::Max(MinDelay, MaxSpawnInterval);
    GetWorldTimerManager().SetTimer(SpawnTimerHandle, this, &ATrafficStartActor::SpawnRandomCar,
        FMath::FRandRange(MinDelay, MaxDelay), false);
}

void ATrafficStartActor::SpawnRandomCar()
{
    if (CarClasses.Num() > 0)
    {
        const TSubclassOf<ATrafficCarActor> CarClass = CarClasses[FMath::RandRange(0, CarClasses.Num() - 1)];
        if (CarClass)
        {
            FActorSpawnParameters SpawnParams;
            SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
            if (ATrafficCarActor* const SpawnedCar = GetWorld()->SpawnActor<ATrafficCarActor>(
                CarClass, GetActorTransform(), SpawnParams))
            {
                UE_LOG(LogTemp, Log, TEXT("Traffic spawn: %s from %s location=%s"),
                    *SpawnedCar->GetName(), *GetName(), *SpawnedCar->GetActorLocation().ToString());
            }
        }
    }
    ScheduleNextSpawn();
}
