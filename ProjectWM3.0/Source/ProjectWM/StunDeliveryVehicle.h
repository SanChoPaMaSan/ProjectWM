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

    /** Server-authoritative. Returns false when this vehicle is already stunned. */
    bool ApplyTrash4Stun(float DurationSeconds = 5.0f);

    /** Assigns HOUSE1 (1/red) or HOUSE2 (2/blue) on the server. */
    void SetTeamIndex(int32 InTeamIndex);

    UFUNCTION(BlueprintPure, Category = "Team")
    int32 GetTeamIndex() const { return TeamIndex; }

    UFUNCTION(BlueprintPure, Category = "Trash4 Stun")
    bool IsStunned() const { return bIsStunned; }

    /**
     * Client request for a trash release.  The selected type is the only
     * client-provided value; the server resolves the actual held Actor from
     * its authoritative inventory before releasing it.
     */
    UFUNCTION(Server, Reliable, BlueprintCallable, Category = "Trash")
    void ServerEjectSelectedTrash(int32 SelectedTrashType);

protected:
    virtual void BeginPlay() override;

    UPROPERTY(ReplicatedUsing = OnRep_IsStunned, BlueprintReadOnly, Category = "Trash4 Stun")
    bool bIsStunned = false;

    UPROPERTY(ReplicatedUsing = OnRep_TeamIndex, BlueprintReadOnly, Category = "Team")
    int32 TeamIndex = 1;

    UFUNCTION()
    void OnRep_IsStunned();

    UFUNCTION()
    void OnRep_TeamIndex();

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

private:
    void ClearTrash4Stun();
    void ApplyLocalInputState();
    void ApplyTeamAppearance();
    bool TakeHeldTrashOnServer(int32 SelectedTrashType, AActor*& OutTrashActor);
    void ReleaseTrashOnServer(AActor* TrashActor);

    UPROPERTY()
    TObjectPtr<class UMaterialInterface> Team1RobotMaterial;

    UPROPERTY()
    TObjectPtr<class UMaterialInterface> Team2RobotMaterial;

    FTimerHandle StunTimerHandle;
};
