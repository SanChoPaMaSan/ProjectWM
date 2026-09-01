#include "StunDeliveryVehicle.h"

#include "Components/MeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/CollisionProfile.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/UnrealType.h"
#include "GameFramework/PlayerController.h"
#include "Net/UnrealNetwork.h"
#include "TimerManager.h"

AStunDeliveryVehicle::AStunDeliveryVehicle()
{
    bReplicates = true;

    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Team1MaterialFinder(
        TEXT("/Game/TeamVisuals/M_Robot_RedMetallic.M_Robot_RedMetallic"));
    static ConstructorHelpers::FObjectFinder<UMaterialInterface> Team2MaterialFinder(
        TEXT("/Game/TeamVisuals/M_Robot_BlueMetallic.M_Robot_BlueMetallic"));

    Team1RobotMaterial = Team1MaterialFinder.Succeeded() ? Team1MaterialFinder.Object : nullptr;
    Team2RobotMaterial = Team2MaterialFinder.Succeeded() ? Team2MaterialFinder.Object : nullptr;
}

void AStunDeliveryVehicle::BeginPlay()
{
    Super::BeginPlay();
    ApplyTeamAppearance();
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

    ReleaseTrashOnServer(TrashActor);
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

void AStunDeliveryVehicle::ReleaseTrashOnServer(AActor* TrashActor)
{
    if (!HasAuthority() || !IsValid(TrashActor))
    {
        return;
    }

    const FVector ReleaseLocation = GetActorLocation() + GetActorForwardVector() * 220.0f + FVector(0.0f, 0.0f, 35.0f);
    TrashActor->SetActorHiddenInGame(false);
    TrashActor->DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
    TrashActor->SetActorLocation(ReleaseLocation, false, nullptr, ETeleportType::TeleportPhysics);

    if (UStaticMeshComponent* TrashMeshComponent = TrashActor->FindComponentByClass<UStaticMeshComponent>())
    {
        TrashMeshComponent->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
        TrashMeshComponent->SetCollisionProfileName(UCollisionProfile::PhysicsActor_ProfileName);
        TrashMeshComponent->SetEnableGravity(true);
        TrashMeshComponent->SetSimulatePhysics(true);
        TrashMeshComponent->AddImpulse(GetActorForwardVector() * 1000.0f + FVector(0.0f, 0.0f, 180.0f), NAME_None, true);
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
}
