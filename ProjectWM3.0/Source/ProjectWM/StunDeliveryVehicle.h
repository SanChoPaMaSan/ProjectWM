#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "StunDeliveryVehicle.generated.h"

/** Character base used by the delivery-vehicle Blueprint for replicated stun. */
UCLASS()
class PROJECTWM_API AStunDeliveryVehicle : public ACharacter
{
    GENERATED_BODY()

public:
    AStunDeliveryVehicle();

    virtual void Tick(float DeltaSeconds) override;

    /** Server-authoritative. Returns false when this vehicle is already stunned. */
    bool ApplyTrash4Stun(float DurationSeconds = 5.0f);

    /** Server-authoritative short displacement from Trash1. */
    void ApplyTrash1Knockback(const FVector& Direction, float Strength = 800.0f);

    /** Server-authoritative 30% movement-speed reduction from Trash2. */
    void ApplyTrash2Slow(float DurationSeconds = 3.0f);

    /** Assigns HOUSE1 (1/red) or HOUSE2 (2/blue) on the server. */
    void SetTeamIndex(int32 InTeamIndex);

    UFUNCTION(BlueprintPure, Category = "Team")
    int32 GetTeamIndex() const { return TeamIndex; }

    UFUNCTION(BlueprintPure, Category = "Trash4 Stun")
    bool IsStunned() const { return bIsStunned; }

    UFUNCTION(BlueprintPure, Category = "Suction")
    float GetSuctionGauge() const { return SuctionGauge; }

    /**
     * Client request for a trash release.  The selected type is the only
     * client-provided value; the server resolves the actual held Actor from
     * its authoritative inventory before releasing it.
     */
    UFUNCTION(Server, Reliable, BlueprintCallable, Category = "Trash")
    void ServerEjectSelectedTrash(int32 SelectedTrashType);

    /** Starts a local-only dotted preview.  It is never replicated to other players. */
    UFUNCTION(BlueprintCallable, Category = "Trash|Trajectory")
    void BeginTrashAim(int32 SelectedTrashType);

    /** Hides the local preview and submits the normal authoritative release request. */
    UFUNCTION(BlueprintCallable, Category = "Trash|Trajectory")
    void ReleaseTrashAimAndEject(int32 SelectedTrashType);

protected:
    virtual void BeginPlay() override;

    UPROPERTY(ReplicatedUsing = OnRep_IsStunned, BlueprintReadOnly, Category = "Trash4 Stun")
    bool bIsStunned = false;

    UPROPERTY(ReplicatedUsing = OnRep_TeamIndex, BlueprintReadOnly, Category = "Team")
    int32 TeamIndex = 1;

    UPROPERTY(ReplicatedUsing = OnRep_IsSlowed, BlueprintReadOnly, Category = "Trash2 Slow")
    bool bIsSlowed = false;

    UFUNCTION()
    void OnRep_IsStunned();

    UFUNCTION()
    void OnRep_TeamIndex();

    UFUNCTION()
    void OnRep_IsSlowed();

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

private:
    FVector GetTrashReleaseLocation() const;
    FVector GetTrashLaunchVelocity(int32 SelectedTrashType) const;
    void EnsureTrajectoryDots();
    void UpdateTrajectoryPreview();
    void HideTrajectoryPreview();
    void UpdateSuctionGauge(float DeltaSeconds);
    void EnsureSuctionGaugeWidget();
    void ClearTrash4Stun();
    void ClearTrash2Slow();
    void ApplySlowMovementState();
    void ApplyLocalInputState();
    void ApplyTeamAppearance();
    bool TakeHeldTrashOnServer(int32 SelectedTrashType, AActor*& OutTrashActor);
    void ReleaseTrashOnServer(AActor* TrashActor, int32 SelectedTrashType);

    UPROPERTY()
    TObjectPtr<class UMaterialInterface> Team1RobotMaterial;

    UPROPERTY()
    TObjectPtr<class UMaterialInterface> Team2RobotMaterial;

    UPROPERTY(Transient)
    TArray<TObjectPtr<class UStaticMeshComponent>> TrajectoryDots;

    UPROPERTY(Transient)
    TObjectPtr<class UStaticMesh> TrajectoryDotMesh;

    UPROPERTY(Transient)
    TObjectPtr<class USuctionGaugeWidget> SuctionGaugeWidget;

    bool bShowingTrajectory = false;
    /** Local lockout: a fully depleted gauge must recover to 20 before another suction press is accepted. */
    bool bSuctionDepletedLockout = false;
    int32 PreviewTrashType = 1;
    float SuctionGauge = 100.0f;
    float TrajectoryPreviewAccumulator = 0.0f;
    static constexpr int32 TrajectoryDotCount = 24;
    static constexpr float TrajectoryPreviewUpdateInterval = 0.05f;

    FTimerHandle StunTimerHandle;
    FTimerHandle SlowTimerHandle;
    float NormalMaxWalkSpeed = 0.0f;
};
