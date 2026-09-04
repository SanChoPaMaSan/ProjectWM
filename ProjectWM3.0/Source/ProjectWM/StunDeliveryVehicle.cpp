#include "StunDeliveryVehicle.h"

#include "Components/MeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/CollisionProfile.h"
#include "Kismet/GameplayStatics.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/UnrealType.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Net/UnrealNetwork.h"
#include "SuctionGaugeWidget.h"
#include "TimerManager.h"
#include "TrashSlowZoneActor.h"

AStunDeliveryVehicle::AStunDeliveryVehicle()
{
    bReplicates = true;
    PrimaryActorTick.bCanEverTick = true;

    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Team1MaterialFinder(
        TEXT("/Game/TeamVisuals/M_Robot_RedMetallic.M_Robot_RedMetallic"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Team2MaterialFinder(
        TEXT("/Game/TeamVisuals/M_Robot_BlueMetallic.M_Robot_BlueMetallic"));

    Team1RobotMaterial = Team1MaterialFinder.Succeeded() ? Team1MaterialFinder.Object : nullptr;
    Team2RobotMaterial = Team2MaterialFinder.Succeeded() ? Team2MaterialFinder.Object : nullptr;

    static ConstructorHelpers::FObjectFinder<UStaticMesh> TrajectoryDotMeshFinder(
        TEXT("/Engine/BasicShapes/Sphere.Sphere"));
    TrajectoryDotMesh = TrajectoryDotMeshFinder.Succeeded() ? TrajectoryDotMeshFinder.Object : nullptr;
}

void AStunDeliveryVehicle::BeginPlay()
{
    Super::BeginPlay();
    if (UCharacterMovementComponent* const Movement = GetCharacterMovement())
    {
        NormalMaxWalkSpeed = Movement->MaxWalkSpeed;
    }
    ApplyTeamAppearance();
}

void AStunDeliveryVehicle::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!bShowingTrajectory || !IsLocallyControlled())
    {
        if (IsLocallyControlled())
        {
            UpdateSuctionGauge(DeltaSeconds);
        }
        return;
    }

    TrajectoryPreviewAccumulator += DeltaSeconds;
    if (TrajectoryPreviewAccumulator >= TrajectoryPreviewUpdateInterval)
    {
        TrajectoryPreviewAccumulator = 0.0f;
        UpdateTrajectoryPreview();
    }

    UpdateSuctionGauge(DeltaSeconds);
}

void AStunDeliveryVehicle::UpdateSuctionGauge(float DeltaSeconds)
{
    FBoolProperty* const SuctionProperty = FindFProperty<FBoolProperty>(GetClass(), TEXT("IsSuctioning"));
    bool bIsSuctioning = SuctionProperty && SuctionProperty->GetPropertyValue_InContainer(this);

    // A held right mouse button must not restart suction by itself after depletion.
    // The player releases and presses again once the gauge has recovered to 20.
    if (bSuctionDepletedLockout)
    {
        if (SuctionProperty)
        {
            SuctionProperty->SetPropertyValue_InContainer(this, false);
        }
        bIsSuctioning = false;
        if (SuctionGauge >= 20.0f)
        {
            bSuctionDepletedLockout = false;
        }
    }

    const float Delta = (bIsSuctioning ? -20.0f : 20.0f) * DeltaSeconds;
    SuctionGauge = FMath::Clamp(SuctionGauge + Delta, 0.0f, 100.0f);

    if (bIsSuctioning && SuctionGauge <= 0.0f)
    {
        SuctionGauge = 0.0f;
        bSuctionDepletedLockout = true;
        if (SuctionProperty)
        {
            SuctionProperty->SetPropertyValue_InContainer(this, false);
        }
    }

    EnsureSuctionGaugeWidget();
    if (SuctionGaugeWidget)
    {
        SuctionGaugeWidget->SetGauge(SuctionGauge);
    }
}

void AStunDeliveryVehicle::EnsureSuctionGaugeWidget()
{
    if (SuctionGaugeWidget || !IsLocallyControlled() || !GetWorld())
    {
        return;
    }

    APlayerController* const PlayerController = Cast<APlayerController>(GetController());
    if (!PlayerController || !PlayerController->IsLocalController())
    {
        return;
    }

    SuctionGaugeWidget = CreateWidget<USuctionGaugeWidget>(PlayerController, USuctionGaugeWidget::StaticClass());
    if (SuctionGaugeWidget)
    {
        SuctionGaugeWidget->AddToViewport(25);
    }
}

void AStunDeliveryVehicle::BeginTrashAim(int32 SelectedTrashType)
{
    if (!IsLocallyControlled() || SelectedTrashType < 1 || SelectedTrashType > 4)
    {
        return;
    }

    PreviewTrashType = SelectedTrashType;
    bShowingTrajectory = true;
    TrajectoryPreviewAccumulator = 0.0f;
    UpdateTrajectoryPreview();
}

void AStunDeliveryVehicle::ReleaseTrashAimAndEject(int32 SelectedTrashType)
{
    HideTrajectoryPreview();

    if (IsLocallyControlled() && SelectedTrashType >= 1 && SelectedTrashType <= 4)
    {
        ServerEjectSelectedTrash(SelectedTrashType);
    }
}

FVector AStunDeliveryVehicle::GetTrashReleaseLocation() const
{
    return GetActorLocation() + GetActorForwardVector() * 220.0f + FVector(0.0f, 0.0f, 35.0f);
}

FVector AStunDeliveryVehicle::GetTrashLaunchVelocity(int32 SelectedTrashType) const
{
    // Keep the preview identical to the server-side AddImpulse(..., true) launch.
    // Trash3 is the long-range box; Trash4 deliberately shares its launch speed.
    if (SelectedTrashType == 3 || SelectedTrashType == 4)
    {
        return GetActorForwardVector() * 1500.0f + FVector(0.0f, 0.0f, 150.0f);
    }
    return GetActorForwardVector() * 1000.0f + FVector(0.0f, 0.0f, 180.0f);
}

void AStunDeliveryVehicle::EnsureTrajectoryDots()
{
    if (!TrajectoryDotMesh || TrajectoryDots.Num() > 0 || !GetRootComponent())
    {
        return;
    }

    for (int32 Index = 0; Index < TrajectoryDotCount; ++Index)
    {
        UStaticMeshComponent* const Dot = NewObject<UStaticMeshComponent>(this);
        Dot->SetStaticMesh(TrajectoryDotMesh);
        Dot->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Dot->SetCastShadow(false);
        Dot->SetReceivesDecals(false);
        Dot->SetHiddenInGame(true);
        Dot->SetVisibility(false);
        Dot->SetWorldScale3D(FVector(0.09f));
        Dot->SetupAttachment(GetRootComponent());
        AddInstanceComponent(Dot);
        Dot->RegisterComponent();
        TrajectoryDots.Add(Dot);
    }
}

void AStunDeliveryVehicle::UpdateTrajectoryPreview()
{
    if (!IsLocallyControlled())
    {
        return;
    }

    EnsureTrajectoryDots();
    if (TrajectoryDots.IsEmpty())
    {
        return;
    }

    FPredictProjectilePathParams Params;
    Params.StartLocation = GetTrashReleaseLocation();
    Params.LaunchVelocity = GetTrashLaunchVelocity(PreviewTrashType);
    Params.MaxSimTime = 2.0f;
    Params.SimFrequency = 30.0f;
    Params.ProjectileRadius = 8.0f;
    Params.bTraceWithCollision = true;
    Params.TraceChannel = ECC_Visibility;
    Params.DrawDebugType = EDrawDebugTrace::None;

    FPredictProjectilePathResult Result;
    UGameplayStatics::PredictProjectilePath(this, Params, Result);

    const int32 PathPointCount = Result.PathData.Num();
    for (int32 DotIndex = 0; DotIndex < TrajectoryDots.Num(); ++DotIndex)
    {
        UStaticMeshComponent* const Dot = TrajectoryDots[DotIndex];
        if (!Dot)
        {
            continue;
        }

        if (PathPointCount > 1 && DotIndex < TrajectoryDotCount)
        {
            const int32 PathIndex = FMath::RoundToInt(
                static_cast<float>(DotIndex) * static_cast<float>(PathPointCount - 1) /
                static_cast<float>(TrajectoryDotCount - 1));
            Dot->SetWorldLocation(Result.PathData[PathIndex].Location);
            Dot->SetHiddenInGame(false);
            Dot->SetVisibility(true);
        }
        else
        {
            Dot->SetHiddenInGame(true);
            Dot->SetVisibility(false);
        }
    }
}

void AStunDeliveryVehicle::HideTrajectoryPreview()
{
    bShowingTrajectory = false;
    TrajectoryPreviewAccumulator = 0.0f;
    for (UStaticMeshComponent* Dot : TrajectoryDots)
    {
        if (Dot)
        {
            Dot->SetHiddenInGame(true);
            Dot->SetVisibility(false);
        }
    }
}

void AStunDeliveryVehicle::SetTeamIndex(int32 InTeamIndex)
{
    if (!HasAuthority())
    {
        return;
    }

    TeamIndex = InTeamIndex == 2 ? 2 : 1;
    ApplyTeamAppearance();
    ForceNetUpdate();
}

void AStunDeliveryVehicle::ServerEjectSelectedTrash_Implementation(int32 SelectedTrashType)
{
    AActor* TrashActor = nullptr;
    if (!TakeHeldTrashOnServer(SelectedTrashType, TrashActor))
    {
        UE_LOG(LogTemp, Warning, TEXT("Trash eject rejected: type %d has no valid server-held Actor."), SelectedTrashType);
        return;
    }

    ReleaseTrashOnServer(TrashActor, SelectedTrashType);
}

bool AStunDeliveryVehicle::TakeHeldTrashOnServer(int32 SelectedTrashType, AActor*& OutTrashActor)
{
    OutTrashActor = nullptr;
    if (!HasAuthority() || SelectedTrashType < 1 || SelectedTrashType > 4)
    {
        return false;
    }

    const FName InventoryName(*FString::Printf(TEXT("HeldTrash%d"), SelectedTrashType));
    const FArrayProperty* InventoryProperty = FindFProperty<FArrayProperty>(GetClass(), InventoryName);
    if (!InventoryProperty)
    {
        UE_LOG(LogTemp, Error, TEXT("Trash eject failed: %s was not found."), *InventoryName.ToString());
        return false;
    }

    const FObjectPropertyBase* ObjectProperty = CastField<FObjectPropertyBase>(InventoryProperty->Inner);
    if (!ObjectProperty)
    {
        UE_LOG(LogTemp, Error, TEXT("Trash eject failed: %s does not store Actors."), *InventoryName.ToString());
        return false;
    }

    FScriptArrayHelper Inventory(InventoryProperty, InventoryProperty->ContainerPtrToValuePtr<void>(this));
    for (int32 Index = Inventory.Num() - 1; Index >= 0; --Index)
    {
        AActor* Candidate = Cast<AActor>(ObjectProperty->GetObjectPropertyValue(Inventory.GetRawPtr(Index)));
        Inventory.RemoveValues(Index, 1);
        if (IsValid(Candidate))
        {
            OutTrashActor = Candidate;
            ForceNetUpdate();
            return true;
        }
    }

    ForceNetUpdate();
    return false;
}

void AStunDeliveryVehicle::ReleaseTrashOnServer(AActor* TrashActor, int32 SelectedTrashType)
{
    if (!HasAuthority() || !IsValid(TrashActor))
    {
        return;
    }

    const FVector ReleaseLocation = GetTrashReleaseLocation();
    if (ATrashSlowZoneActor* const SlowTrash = Cast<ATrashSlowZoneActor>(TrashActor))
    {
        // BP_Trash2 may touch the floor while it is first spawned; arm its effect only for a player release.
        SlowTrash->ArmSlowZoneForThrow();
    }
    TrashActor->SetActorHiddenInGame(false);
    TrashActor->DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
    TrashActor->SetActorLocation(ReleaseLocation, false, nullptr, ETeleportType::TeleportPhysics);

    if (UStaticMeshComponent* TrashMeshComponent = TrashActor->FindComponentByClass<UStaticMeshComponent>())
    {
        TrashMeshComponent->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
        TrashMeshComponent->SetCollisionProfileName(UCollisionProfile::PhysicsActor_ProfileName);
        TrashMeshComponent->SetEnableGravity(true);
        TrashMeshComponent->SetSimulatePhysics(true);
        TrashMeshComponent->AddImpulse(GetTrashLaunchVelocity(SelectedTrashType), NAME_None, true);
        if (SelectedTrashType == 3)
        {
            // Pizza box: spin flat like a thrown shuriken while it travels.
            TrashMeshComponent->SetPhysicsAngularVelocityInDegrees(FVector(0.0f, 0.0f, 1440.0f), false);
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Trash eject failed: %s has no StaticMeshComponent."), *TrashActor->GetName());
    }

    TrashActor->SetReplicateMovement(true);
    TrashActor->ForceNetUpdate();
    ForceNetUpdate();
}

bool AStunDeliveryVehicle::ApplyTrash4Stun(float DurationSeconds)
{
    if (!HasAuthority() || bIsStunned)
    {
        return false;
    }

    bIsStunned = true;
    ApplyLocalInputState();

    const float SafeDuration = FMath::Max(0.1f, DurationSeconds);
    GetWorldTimerManager().SetTimer(StunTimerHandle, this, &AStunDeliveryVehicle::ClearTrash4Stun, SafeDuration, false);
    ForceNetUpdate();
    return true;
}

void AStunDeliveryVehicle::ApplyTrash1Knockback(const FVector& Direction, float Strength)
{
    if (!HasAuthority())
    {
        return;
    }

    const FVector LaunchVelocity = Direction.GetSafeNormal2D() * Strength + FVector(0.0f, 0.0f, 160.0f);
    LaunchCharacter(LaunchVelocity, true, true);
}

void AStunDeliveryVehicle::ApplyTrash2Slow(float DurationSeconds)
{
    if (!HasAuthority())
    {
        return;
    }

    bIsSlowed = true;
    ApplySlowMovementState();
    GetWorldTimerManager().SetTimer(SlowTimerHandle, this, &AStunDeliveryVehicle::ClearTrash2Slow,
        FMath::Max(0.1f, DurationSeconds), false);
    ForceNetUpdate();
}

void AStunDeliveryVehicle::ClearTrash2Slow()
{
    if (!HasAuthority())
    {
        return;
    }

    bIsSlowed = false;
    ApplySlowMovementState();
    ForceNetUpdate();
}

void AStunDeliveryVehicle::OnRep_IsSlowed()
{
    ApplySlowMovementState();
}

void AStunDeliveryVehicle::ApplySlowMovementState()
{
    if (UCharacterMovementComponent* const Movement = GetCharacterMovement())
    {
        if (NormalMaxWalkSpeed <= 0.0f)
        {
            NormalMaxWalkSpeed = Movement->MaxWalkSpeed;
        }
        Movement->MaxWalkSpeed = NormalMaxWalkSpeed * (bIsSlowed ? 0.7f : 1.0f);
    }
}

void AStunDeliveryVehicle::ClearTrash4Stun()
{
    if (!HasAuthority())
    {
        return;
    }

    bIsStunned = false;
    ApplyLocalInputState();
    ForceNetUpdate();
}

void AStunDeliveryVehicle::OnRep_IsStunned()
{
    ApplyLocalInputState();
}

void AStunDeliveryVehicle::OnRep_TeamIndex()
{
    ApplyTeamAppearance();
}

void AStunDeliveryVehicle::ApplyLocalInputState()
{
    if (!IsLocallyControlled())
    {
        return;
    }

    if (APlayerController* PlayerController = Cast<APlayerController>(GetController()))
    {
        if (bIsStunned)
        {
            DisableInput(PlayerController);
        }
        else
        {
            EnableInput(PlayerController);
        }
    }
}

void AStunDeliveryVehicle::ApplyTeamAppearance()
{
    UMaterialInterface* const TeamMaterial = TeamIndex == 2 ? Team2RobotMaterial : Team1RobotMaterial;
    if (!TeamMaterial)
    {
        return;
    }

    TArray<UMeshComponent*> MeshComponents;
    GetComponents(MeshComponents);
    for (UMeshComponent* MeshComponent : MeshComponents)
    {
        if (!IsValid(MeshComponent))
        {
            continue;
        }

        const int32 MaterialCount = MeshComponent->GetNumMaterials();
        for (int32 MaterialIndex = 0; MaterialIndex < MaterialCount; ++MaterialIndex)
        {
            MeshComponent->SetMaterial(MaterialIndex, TeamMaterial);
        }
    }
}

void AStunDeliveryVehicle::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AStunDeliveryVehicle, bIsStunned);
    DOREPLIFETIME(AStunDeliveryVehicle, TeamIndex);
    DOREPLIFETIME(AStunDeliveryVehicle, bIsSlowed);
}
