```markdown
# Design System Document

## 1. Overview & Creative North Star: "The Ethereal Guide"

This design system moves away from the rigid, boxy constraints of traditional gaming apps to embrace **The Ethereal Guide**. This North Star prioritizes a high-end editorial feel where the AI assistant isn't just a feature, but a presence. 

The aesthetic is defined by **Soft Minimalism**: a rejection of heavy borders and loud "gamey" gradients in favor of high-contrast typography, vast "breathing room," and layered depth. We break the template look by using intentional asymmetry—shifting text alignments and using overlapping surfaces—to create a sense of organic movement. The goal is an interface that feels less like a software tool and more like a premium, physical stationery set floating in a digital space.

---

## 2. Colors: Tonal Depth over Borders

Our palette relies on a sophisticated interplay of mint greens and soft cyans, anchored by a rich "on-surface" slate.

### The "No-Line" Rule
**Designers are strictly prohibited from using 1px solid borders for sectioning.** Hierarchy must be established through background shifts. For instance, a `surface-container-low` input area should sit directly against a `surface` background. The eye should perceive boundaries through color temperature changes, not mechanical lines.

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked, semi-transparent sheets:
- **Base Layer:** `surface` (#f8f9fa) or `surface-container-lowest` (#ffffff).
- **Secondary Content:** Use `surface-container` to pull peripheral information back.
- **Interactive Elements:** Use `surface-bright` to draw the eye forward.
- **The Glass & Gradient Rule:** For the AI "Agent" bubbles or floating game stats, use Glassmorphism. Apply `surface-variant` at 60% opacity with a `20px` backdrop-blur.

### Signature Textures
Main CTAs (Primary) should not be flat. Use a subtle linear gradient from `primary` (#006c5a) to `primary_fixed_dim` (#7ae8cc) at a 135-degree angle to give buttons a "gem-like" physical presence.

---

## 3. Typography: Editorial Authority

We pair **Plus Jakarta Sans** (Display/Headlines) with **Inter** (Body/Labels) to balance character with extreme legibility.

- **Display & Headlines (Plus Jakarta Sans):** These are our "Editorial Voice." Use `display-md` for game wins or major milestones. The tighter letter-spacing and higher x-height of Plus Jakarta Sans provide a premium, modern feel.
- **Body & Titles (Inter):** Our "Functional Voice." Inter handles the chat-style interaction and word-guessing logic. 
- **The Hierarchy Strategy:** Use `headline-sm` for the AI's prompts to give them authority, while the user’s input remains in `title-md` for a clear, conversational distinction.

---

## 4. Elevation & Depth: Tonal Layering

Traditional shadows are often a crutch for poor layout. In this system, we prioritize **Tonal Layering**.

- **The Layering Principle:** To lift a card, place a `surface-container-lowest` (#ffffff) card on top of a `surface-container-low` (#f1f4f5) background. The 2-point difference in hex value provides a sophisticated, natural lift.
- **Ambient Shadows:** When a floating state is required (e.g., a modal or a floating action button), use an ultra-diffused shadow: `box-shadow: 0 12px 40px rgba(45, 51, 53, 0.06)`. The shadow color is derived from `on-surface`, not pure black.
- **The "Ghost Border" Fallback:** If accessibility requires a stroke (e.g., in high-contrast modes), use the `outline-variant` token at **15% opacity**. It should be felt, not seen.

---

## 5. Components: Intentional Primitives

### Buttons
- **Primary:** Gradient-filled (Primary to Primary-Fixed-Dim) with `xl` (1.5rem) rounded corners. Use `on-primary` for text.
- **Secondary:** `secondary-container` background with `on-secondary-container` text. No border.
- **Tertiary:** Pure text using `primary` color, sitting on a transparent background.

### Chat Bubbles (The "Agent" Interaction)
- **Agent Bubble:** Use `tertiary-container` (Pastel Yellow) with `xl` rounding on all corners except the bottom-left.
- **User Bubble:** Use `surface-container-highest` with `xl` rounding on all corners except the bottom-right.
- **Spacing:** Avoid dividers. Use a `1.5rem` vertical gap between different speakers and `0.5rem` between consecutive bubbles from the same speaker.

### Input Fields
- **Container:** `surface-container-low` with a `md` (0.75rem) radius.
- **Interaction:** On focus, the background transitions to `surface-container-lowest` and a subtle 2px "Ghost Border" of `primary` at 20% opacity appears.

### Progress & Feedback Chips
- **Success:** `primary-container` background with `on-primary-fixed` text.
- **Error:** `error-container` background with `on-error-container` text.
- **The Animation:** Chips should "fade-slide" in from the bottom with a 300ms cubic-bezier (0.34, 1.56, 0.64, 1) timing.

---

## 6. Do's and Don'ts

### Do
- **Do** use whitespace as a structural element. If you think you need a line, try adding 16px of padding instead.
- **Do** use `plusJakartaSans` for all numerical game scores to make them feel like "rewards."
- **Do** leverage the `xl` (1.5rem) corner radius for main containers to maintain the "friendly" game persona.

### Don't
- **Don't** use pure black (#000000) for text. Always use `on-surface` (#2d3335) to maintain the soft, premium feel.
- **Don't** use standard Material Design elevation shadows (1dp, 2dp). Stick to Tonal Layering or the Ambient Shadow spec.
- **Don't** center-align long passages of text. Keep game instructions left-aligned (Editorial style) for better readability.

---

## 7. Contextual Component: The "Hunch" Card
Unique to this app, the **Hunch Card** (where the AI gives a hint) should use the **Glassmorphism** rule. It should overlay the game board with a `surface-container-highest` 40% opacity blur, using `tertiary` (Yellow) accents to signify the Assistant's presence. Use `title-lg` for the hint text to ensure it feels like a significant "moment" in the gameplay.```