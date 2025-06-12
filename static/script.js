let correctAnswers = [];
document.getElementById("uploadForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    let formData = new FormData();
    formData.append("file", document.getElementById("pdfFile").files[0]);
    formData.append("num_questions", document.getElementById("numQuestions").value);

    let response = await fetch("/generate", {
        method: "POST",
        body: formData
    });

    let mcqs = await response.json();
    correctAnswers = mcqs.map(mcq => mcq.answer); // Store correct answers

    let mcqContainer = document.getElementById("mcqContainer");
    mcqContainer.innerHTML = "<h4 class='text-white'>Generated MCQs:</h4>";

    mcqs.forEach((mcq, index) => {
        let questionHTML = `<div class='card p-3 mt-2' id='question-${index}'><strong>Q${index + 1}: ${mcq.question}</strong><br>`;
        mcq.options.forEach(option => {
            questionHTML += `<input type='radio' name='q${index}' value='${option}'> ${option}<br>`;
        });
        questionHTML += `</div>`;
        mcqContainer.innerHTML += questionHTML;
    });

    mcqContainer.innerHTML += `<button id='submitAnswers' class='btn btn-success mt-3'>Submit Answers</button>`;

    document.getElementById("submitAnswers").addEventListener("click", showResults);
});

function showResults() {
    let score = 0;

    correctAnswers.forEach((answer, index) => {
        let options = document.getElementsByName(`q${index}`);
        let selected = null;
        options.forEach(option => {
            if (option.checked) selected = option.value;
        });

        const container = document.getElementById(`question-${index}`);

        if (selected === answer) {
            score++;
            container.style.border = "4px solid green";
        } else {
            container.style.border = "4px solid red";
            // container.innerHTML += `<div class="text-white">Correct Answer: <strong>${answer}</strong></div>`;
        
        
        container.innerHTML += `<div class="correct-answer">Correct Answer: <strong>${answer}</strong></div>`;

        }
    });


    const resultDiv = document.createElement("div");
    resultDiv.innerHTML = `<h5 class="text-black mt-3">Your Score: ${score}/${correctAnswers.length}</h5>`;
    document.getElementById("mcqContainer").appendChild(resultDiv);
}
