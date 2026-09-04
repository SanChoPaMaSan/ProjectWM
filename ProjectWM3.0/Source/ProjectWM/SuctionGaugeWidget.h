#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "SuctionGaugeWidget.generated.h"

class UProgressBar;
class UTextBlock;

/** Local HUD overlay for the delivery vehicle's suction resource. */
UCLASS()
class PROJECTWM_API USuctionGaugeWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    void SetGauge(float Value);

protected:
    virtual void NativeOnInitialized() override;

private:
    void BuildWidgetTree();

    UPROPERTY()
    TObjectPtr<UProgressBar> GaugeBar;

    UPROPERTY()
    TObjectPtr<UTextBlock> GaugeValueText;
};
