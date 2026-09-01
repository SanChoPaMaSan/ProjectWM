#include "GameResultWidget.h"

#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/Overlay.h"
#include "Components/OverlaySlot.h"
#include "Components/Spacer.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/KismetSystemLibrary.h"

namespace
{
UTextBlock* AddCenteredText(UWidgetTree* WidgetTree, UVerticalBox* Parent, const FString& Text, int32 Size, const FLinearColor& Color)
{
    UTextBlock* TextBlock = WidgetTree->ConstructWidget<UTextBlock>();
    TextBlock->SetText(FText::FromString(Text));
    TextBlock->SetColorAndOpacity(FSlateColor(Color));
    TextBlock->SetJustification(ETextJustify::Center);

    FSlateFontInfo Font = TextBlock->GetFont();
    Font.Size = Size;
    Font.TypefaceFontName = TEXT("Bold");
    TextBlock->SetFont(Font);

    UVerticalBoxSlot* Slot = Parent->AddChildToVerticalBox(TextBlock);
    Slot->SetHorizontalAlignment(HAlign_Fill);
    Slot->SetPadding(FMargin(8.0f));
    return TextBlock;
}

void AddSpace(UWidgetTree* WidgetTree, UVerticalBox* Parent, float Height)
{
    USpacer* Spacer = WidgetTree->ConstructWidget<USpacer>();
    Spacer->SetSize(FVector2D(1.0f, Height));
    Parent->AddChildToVerticalBox(Spacer);
}
}

void UGameResultWidget::NativeOnInitialized()
{
    Super::NativeOnInitialized();
    BuildWidgetTree();
}

void UGameResultWidget::BuildWidgetTree()
{
    if (!WidgetTree || WidgetTree->RootWidget)
    {
        return;
    }

    UOverlay* Root = WidgetTree->ConstructWidget<UOverlay>();
    WidgetTree->RootWidget = Root;

    UBorder* Dimmer = WidgetTree->ConstructWidget<UBorder>();
    Dimmer->SetBrushColor(FLinearColor(0.0f, 0.0f, 0.0f, 0.78f));
    UOverlaySlot* DimmerSlot = Root->AddChildToOverlay(Dimmer);
    DimmerSlot->SetHorizontalAlignment(HAlign_Fill);
    DimmerSlot->SetVerticalAlignment(VAlign_Fill);

    UBorder* Panel = WidgetTree->ConstructWidget<UBorder>();
    Panel->SetBrushColor(FLinearColor(0.015f, 0.045f, 0.09f, 0.97f));
    Panel->SetPadding(FMargin(50.0f, 38.0f));
    UOverlaySlot* PanelSlot = Root->AddChildToOverlay(Panel);
    PanelSlot->SetHorizontalAlignment(HAlign_Center);
    PanelSlot->SetVerticalAlignment(VAlign_Center);

    UVerticalBox* Content = WidgetTree->ConstructWidget<UVerticalBox>();
    Panel->SetContent(Content);

    AddCenteredText(WidgetTree, Content, TEXT("게임 종료"), 46, FLinearColor(0.25f, 0.9f, 1.0f, 1.0f));
    AddSpace(WidgetTree, Content, 12.0f);
    OutcomeText = AddCenteredText(WidgetTree, Content, TEXT("승리"), 70, FLinearColor(0.15f, 0.9f, 1.0f, 1.0f));
    AddSpace(WidgetTree, Content, 24.0f);
    OurScoreText = AddCenteredText(WidgetTree, Content, TEXT("우리팀 점수  0"), 34, FLinearColor(0.15f, 0.75f, 1.0f, 1.0f));
    OpponentScoreText = AddCenteredText(WidgetTree, Content, TEXT("상대팀 점수  0"), 34, FLinearColor(1.0f, 0.3f, 0.32f, 1.0f));
    AddSpace(WidgetTree, Content, 26.0f);

    QuitButton = WidgetTree->ConstructWidget<UButton>();
    QuitButton->SetBackgroundColor(FLinearColor(0.05f, 0.5f, 0.75f, 1.0f));
    QuitButton->OnClicked.AddDynamic(this, &UGameResultWidget::HandleQuitClicked);
    UVerticalBoxSlot* ButtonSlot = Content->AddChildToVerticalBox(QuitButton);
    ButtonSlot->SetHorizontalAlignment(HAlign_Fill);
    ButtonSlot->SetPadding(FMargin(70.0f, 8.0f));

    UTextBlock* ButtonText = WidgetTree->ConstructWidget<UTextBlock>();
    ButtonText->SetText(FText::FromString(TEXT("게임 종료하기")));
    ButtonText->SetJustification(ETextJustify::Center);
    ButtonText->SetColorAndOpacity(FSlateColor(FLinearColor::White));
    FSlateFontInfo ButtonFont = ButtonText->GetFont();
    ButtonFont.Size = 30;
    ButtonFont.TypefaceFontName = TEXT("Bold");
    ButtonText->SetFont(ButtonFont);
    ButtonText->SetMargin(FMargin(24.0f, 14.0f));
    QuitButton->SetContent(ButtonText);
}

void UGameResultWidget::SetResult(int32 InOurScore, int32 InOpponentScore)
{
    if (!OutcomeText || !OurScoreText || !OpponentScoreText)
    {
        return;
    }

    OurScoreText->SetText(FText::FromString(FString::Printf(TEXT("우리팀 점수  %d"), InOurScore)));
    OpponentScoreText->SetText(FText::FromString(FString::Printf(TEXT("상대팀 점수  %d"), InOpponentScore)));

    if (InOurScore > InOpponentScore)
    {
        OutcomeText->SetText(FText::FromString(TEXT("승리")));
        OutcomeText->SetColorAndOpacity(FSlateColor(FLinearColor(0.15f, 0.9f, 1.0f, 1.0f)));
    }
    else if (InOurScore < InOpponentScore)
    {
        OutcomeText->SetText(FText::FromString(TEXT("패배")));
        OutcomeText->SetColorAndOpacity(FSlateColor(FLinearColor(1.0f, 0.25f, 0.3f, 1.0f)));
    }
    else
    {
        OutcomeText->SetText(FText::FromString(TEXT("무승부")));
        OutcomeText->SetColorAndOpacity(FSlateColor(FLinearColor(0.95f, 0.85f, 0.35f, 1.0f)));
    }
}

void UGameResultWidget::HandleQuitClicked()
{
    if (APlayerController* PlayerController = GetOwningPlayer())
    {
        UKismetSystemLibrary::QuitGame(this, PlayerController, EQuitPreference::Quit, false);
    }
}
