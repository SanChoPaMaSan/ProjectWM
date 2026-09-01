#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "LobbyPlayerController.generated.h"

class ULobbyMenuWidget;
class UGameResultWidget;

UCLASS()
class PROJECTWM_API ALobbyPlayerController : public APlayerController
{
    GENERATED_BODY()

public:
    ALobbyPlayerController();

    UFUNCTION(Client, Reliable)
    void ClientShowMatchResult(int32 OurScore, int32 OpponentScore);

    UFUNCTION(Client, Reliable)
    void ClientAssignTeamIndex(int32 TeamIndex);

protected:
    virtual void BeginPlay() override;
    virtual void BeginPlayingState() override;
    virtual void PostSeamlessTravel() override;

private:
    void ConfigureForCurrentMap();
    void ApplyPendingTeamIndex();

    UPROPERTY()
    TObjectPtr<ULobbyMenuWidget> LobbyWidget;

    UPROPERTY()
    TSubclassOf<ULobbyMenuWidget> LobbyMenuClass;

    UPROPERTY()
    TObjectPtr<UGameResultWidget> GameResultWidget;

    int32 PendingTeamIndex = 0;
    int32 TeamIndexApplyAttempts = 0;
    FTimerHandle TeamIndexApplyTimerHandle;
};
