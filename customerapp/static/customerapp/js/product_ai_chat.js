document.addEventListener("DOMContentLoaded", function () {

    const btn = document.getElementById("askAiBtn");

    btn.addEventListener("click", function () {

        const question =
            document.getElementById("aiQuestion").value;

        if (question.trim() == "") {

            alert("Please ask a question.");

            return;
        }

        const formData = new FormData();

        formData.append(
            "product_id",
            document.getElementById("product_id").value
        );

        formData.append(
            "question",
            question
        );

        formData.append(
            "csrfmiddlewaretoken",
            document.querySelector("[name=csrfmiddlewaretoken]").value
        );

        btn.disabled = true;

        btn.innerHTML = "⏳ Thinking...";

        fetch("/customer/ask-ai/", {

            method: "POST",

            body: formData

        })

        .then(res => res.json())

        .then(res => {

            btn.disabled = false;

            btn.innerHTML = "Ask AI";

            if (!res.success) {

                alert(res.message);

                return;

            }

            const ans =
                document.getElementById("aiAnswer");

            ans.style.display = "block";

            ans.innerHTML = res.answer;

        })

        .catch(err => {

            btn.disabled = false;

            btn.innerHTML = "Ask AI";

            alert("Something went wrong.");

            console.log(err);

        });

    });

});