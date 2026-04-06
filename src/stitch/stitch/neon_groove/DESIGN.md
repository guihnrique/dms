# Design System Document: The Sonic Immersive

## 1. Overview & Creative North Star: "The Neon Pulse"
This design system is engineered to transcend the transactional nature of e-commerce, turning music discovery into a high-end, immersive experience. Our Creative North Star is **"The Neon Pulse"**—a philosophy that treats the interface not as a static grid, but as a living, breathing digital venue. 

To achieve this, we reject "template" layouts. We embrace **Intentional Asymmetry**, where hero elements might break the container, and **Tonal Depth**, where the UI feels like layered sheets of obsidian and violet glass. We aren't just selling audio; we are visualizing the energy of sound through high-contrast typography and glowing accents.

---

## 2. Colors: Depth and Vibration
Our palette is rooted in a deep, nocturnal base (`#1b0424`), allowing our neon accents to "pop" with an almost backlit intensity.

### The "No-Line" Rule
**Borders are forbidden for structural sectioning.** We do not use 1px solid lines to separate content. Boundaries must be defined through:
- **Background Shifts:** Placing a `surface_container_low` card on a `surface` background.
- **Tonal Transitions:** Subtle shifts between `surface_container` tiers.

### Surface Hierarchy & Nesting
Treat the UI as physical layers of glass.
- **Base Layer:** `surface` (#1b0424).
- **Secondary Sectioning:** `surface_container_low` (#22062c).
- **Interactive Cards:** `surface_container` (#2a0b35).
- **Floating/Active Elements:** `surface_bright` (#421b4f).

### The "Glass & Gradient" Rule
To capture the "modern/innovative" requirement, use **Glassmorphism** for navigation bars and floating music players. Use `surface_variant` with a 60% opacity and a `20px` backdrop-blur. 
**Signature Gradients:** For primary actions, use a linear gradient from `primary_dim` (#a533ff) to `secondary` (#00d2fd). This creates a "electric" transition that flat colors cannot replicate.

---

## 3. Typography: Editorial Authority
We pair the technical precision of **Space Grotesk** with the clean, humanistic flow of **Manrope**.

*   **Display & Headlines (Space Grotesk):** Use `display-lg` (3.5rem) for artist names and major promotions. The wide tracking and geometric shapes of Space Grotesk should feel like a high-end music magazine.
*   **Titles & Body (Manrope):** Use `title-md` for track names and `body-md` for descriptions. Manrope ensures maximum legibility against dark backgrounds.
*   **Hierarchy Tip:** Always use `on_surface_variant` (#c39fca) for secondary metadata (like "Album • 2024") to create a clear visual step down from the primary `on_surface` white.

---

## 4. Elevation & Depth: Tonal Layering
In this design system, shadows are light, and depth is felt, not seen.

*   **The Layering Principle:** Instead of shadows, stack containers. An artist's bio card (`surface_container_high`) should sit atop a background section (`surface_container_low`). The color difference provides the "lift."
*   **Ambient Shadows:** For floating modals, use a custom shadow: `0px 20px 40px rgba(0, 0, 0, 0.4)`. The shadow should be tinted with the background hue, never pure black.
*   **The "Ghost Border" Fallback:** If a boundary is required for accessibility, use `outline_variant` (#5a3d62) at **15% opacity**. It should be a whisper of a line.
*   **Glassmorphism Depth:** Elements using backdrop-blur should have a `1px` inner-glow border using `outline` at 20% opacity to simulate the edge of a glass pane.

---

## 5. Components: Modern Primitives

### Buttons
- **Primary (The Power Move):** Rounded `full` (9999px). Gradient fill (`primary_dim` to `secondary`). Label in `on_primary_fixed` (Black) for maximum punch.
- **Secondary (The Glass Button):** Transparent background, `1px` ghost border, text in `secondary`.
- **Tertiary:** No background. Text in `primary` with a subtle hover glow.

### Cards (Album/Artist)
- **Rule:** Forbid divider lines. 
- **Style:** Use `xl` (1.5rem) rounded corners. Image takes top priority. Background is `surface_container`. On hover, the card should scale (1.02x) and the background should shift to `surface_bright`.

### Music Player Bar (Signature Component)
- **Visuals:** Fixed at the bottom. Background is `surface_container` at 80% opacity with a `24px` blur. 
- **Progress Bar:** Base track in `outline_variant`, active progress in a `secondary` to `tertiary` gradient.

### Input Fields
- **Style:** Minimalist. `surface_container_lowest` background. No border, only a `2px` bottom-accent in `primary` when focused. 

---

## 6. Do's and Don'ts

### Do:
- **Do use Spacing Scale 12 and 16** for major section breathing room. High-end design requires "wasted" space.
- **Do use Overlapping Elements.** Let an album cover slightly overlap a headline to create depth.
- **Do use Vibrant Accents sparingly.** Use `tertiary` (#ff6b98) for "Live" tags or "Sale" badges only.

### Don't:
- **Don't use pure black (#000000).** Our base is the deep violet of `background`. Pure black kills the "immersive" atmosphere.
- **Don't use standard icons.** Use thin-stroke (1.5px) custom icons to match the sophistication of Space Grotesk.
- **Don't use 90-degree corners.** Everything must have at least a `md` (0.75rem) radius to maintain the modern, fluid feel.