// Copy buttons ([data-copy]): the clicked button shows "Copied!" until another copy
// button is clicked. A denied clipboard reveals the text, selected, for manual copying.
export function copyButtons(): void {
  const fallback = document.createElement("span")
  fallback.className = "copy-fallback"
  fallback.innerHTML = `<span role="status"></span><textarea rows="4" readonly aria-label="Text to copy"></textarea>`
  const status = fallback.querySelector("span")!
  const textarea = fallback.querySelector("textarea")!
  let resetCopied = () => {}

  for (const button of document.querySelectorAll<HTMLButtonElement>("[data-copy]")) {
    const label = button.textContent!.trim()
    const contents = button.innerHTML
    const accessibleLabel = button.getAttribute("aria-label") ?? label
    button.addEventListener("click", async () => {
      const text = button.dataset.copy!
      resetCopied()
      fallback.remove()
      button.style.inlineSize = `${button.getBoundingClientRect().width}px`
      const reset = () => {
        button.innerHTML = contents
        button.setAttribute("aria-label", accessibleLabel)
        button.classList.remove("is-copied")
        button.style.removeProperty("inline-size")
      }
      resetCopied = reset
      try {
        await navigator.clipboard.writeText(text)
        if (resetCopied !== reset) return
        if (!button.hasAttribute("data-copy-icon")) button.textContent = "Copied!"
        button.setAttribute("aria-label", "Copied!")
        button.classList.add("is-copied")
      } catch {
        if (resetCopied !== reset) return
        reset()
        const anchor = button.parentElement instanceof HTMLParagraphElement ? button.parentElement : button
        anchor.after(fallback)
        textarea.value = text
        textarea.select()
        status.textContent = "Copy failed. The text is selected below, copy it manually."
      }
    })
  }
}
