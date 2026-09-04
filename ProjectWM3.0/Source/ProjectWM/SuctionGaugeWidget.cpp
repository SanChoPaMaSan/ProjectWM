#include "SuctionGaugeWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ProgressBar.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"

void USuctionGaugeWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    BuildWidgetTree();
    SetGauge(100.0f);
}

void USuctionGaugeWidget::BuildWidgetTree()
{
    if (!WidgetTree || WidgetTree->RootWidget)
    {
        return;
    }

    UCanvasPanel* Root = WidgetTree->ConstructWidget<UCanvasPanel>();
    WidgetTree->RootWidget = Root;

    UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
    Panel->SetBrushColor(FLinearColor(0.01f, 0.04f, 0.08f, 0.86f));
    Panel->SetPadding(FMargin(10.0f, 7.0f));
    UCanvasPanelSlot* PanelSlot = Root->AddChildToCanvas(Panel);
    PanelSlot->SetAnchors(FAnchors(1.0f, 0.0f));
    PanelSlot->SetAlignment(FVector2D(1.0f, 0.0f));
    // The existing booster panel occupies the upper-right corner; this sits below it.
    PanelSlot->SetPosition(FVector2D(-28.0f, 180.0f));
    PanelSlot->SetSize(FVector2D(260.0f, 62.0f));

    UVerticalBox* Content = WidgetTree->ConstructWidget<UVerticalBox>();
    Panel->SetContent(Content);

    UTextBlock* Title = WidgetTree->ConstructWidget<UTextBlock>();
    Title->SetText(FText::FromString(TEXT("흡수 게이지")));
    Title->SetColorAndOpacity(FSlateColor(FLinearColor(0.45f, 0.9f, 1.0f, 1.0f)));
    FSlateFontInfo TitleFont = Title->GetFont();
    TitleFont.Size = 17;
    TitleFont.TypefaceFontName = TEXT("Bold");
    Title->SetFont(TitleFont);
    Content->AddChildToVerticalBox(Title);

    GaugeBar = WidgetTree->ConstructWidget<UProgressBar>();
    GaugeBar->SetPercent(1.0f);
    GaugeBar->SetFillColorAndOpacity(FLinearColor(0.08f, 0.75f, 1.0f, 1.0f));
    UVerticalBoxSlot* GaugeSlot = Content->AddChildToVerticalBox(GaugeBar);
    GaugeSlot->SetPadding(FMargin(0.0f, 4.0f, 0.0f, 0.0f));

    GaugeValueText = WidgetTree->ConstructWidget<UTextBlock>();
    GaugeValueText->SetColorAndOpacity(FSlateColor(FLinearColor::White));
    GaugeValueText->SetJustification(ETextJustify::Right);
    FSlateFontInfo ValueFont = GaugeValueText->GetFont();
    ValueFont.Size = 14;
    GaugeValueText->SetFont(ValueFont);
    Content->AddChildToVerticalBox(GaugeValueText);
}

void USuctionGaugeWidget::SetGauge(float Value)
{
    const float ClampedValue = FMath::Clamp(Value, 0.0f, 100.0f);
    if (GaugeBar)
    {
        GaugeBar->SetPercent(ClampedValue / 100.0f);
        GaugeBar->SetFillColorAndOpacity(
            ClampedValue > 25.0f
                ? FLinearColor(0.08f, 0.75f, 1.0f, 1.0f)
                : FLinearColor(1.0f, 0.22f, 0.16f, 1.0f));
    }
    if (GaugeValueText)
    {
        GaugeValueText->SetText(FText::FromString(FString::Printf(TEXT("%d / 100"), FMath::RoundToInt(ClampedValue))));
    }
}
