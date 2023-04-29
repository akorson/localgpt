document.addEventListener("DOMContentLoaded", () => {
  // Get DOM elements
  const inputField = document.getElementById("inputField");
  const submitBtn = document.getElementById("submitBtn");
  const outputField = document.getElementById("outputField");
  const characterCount = document.getElementById("characterCount");

  // Update character count
  inputField.addEventListener("input", () => {
    characterCount.textContent = inputField.value.length;
  });

  // Generate text from OpenAI API
  submitBtn.addEventListener("click", async () => {
    const prompt = inputField.value;
    if (!prompt) return;

    submitBtn.disabled = true;
    submitBtn.textContent = "Generating...";

    try {
      const response = await fetch("/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt }),
      });

      if (response.ok) {
        const data = await response.json();
        outputField.textContent = data.generated_text;
      } else {
        throw new Error("Server error");
      }
    } catch (error) {
      console.error(error);
      outputField.textContent = `Error generating text: ${error.message}`;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Generate";
    }
  });
});
