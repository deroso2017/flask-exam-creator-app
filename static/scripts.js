function toggleAnswer(id) {
  const answerDiv = document.getElementById(`answer-${id}`);
  const button = event.target;

  if (answerDiv.classList.contains("hidden")) {
    answerDiv.classList.remove("hidden");
    button.textContent = "Hide Answer";
  } else {
    answerDiv.classList.add("hidden");
    button.textContent = "Show Answer";
  }
}
