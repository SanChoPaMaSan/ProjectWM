#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "GameResultWidget.generated.h"

class UButton;
class UTextBlock;

UCLASS()
class PROJECTWM_API UGameResultWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    void SetResult(int32 InOurScore, int32 InOpponentScore);

protected:
    virtual void NativeOnInitialized() override;

private:
    void BuildWidgetTree();

    UFUNCTION()
    void HandleQuitClicked();

    UPROPERTY()
    TObjectPtr<UTextBlock> OutcomeText;

    UPROPERTY()
    TObjectPtr<UTextBlock> OurScoreText;

    UPROPERTY()
    TObjectPtr<UTextBlock> OpponentScoreText;

    UPROPERTY()
    TObjectPtr<UButton> QuitButton;
};
