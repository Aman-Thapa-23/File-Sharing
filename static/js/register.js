//Email Validation Start
const EmailField = document.querySelector("#EmailField");
const EmailFeedBackArea = document.querySelector(".emailFeedBackArea");
const EmailSuccessOutput = document.querySelector(".EmailSuccessOutput");

const SubmitBtn = document.querySelector(".submit-btn");

EmailField.addEventListener("keyup", EmailFieldValidate);
function EmailFieldValidate(event) {
  const emailval = event.target.value;

  EmailSuccessOutput.style.display = "block";
  EmailSuccessOutput.textContent = `Checking ${emailval}`;

  EmailField.classList.remove("is-invalid");
  EmailFeedBackArea.style.display = "none";

  if (emailval.length > 0) {

    fetch("/users/email-validate", {
      body: JSON.stringify({ email: emailval }),
      method: "POST",
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("data", data);
        EmailSuccessOutput.style.display = "none";
        if (data.email_error){
          // alert(data.email_error)
          SubmitBtn.setAttribute("disabled", "disabled");
          EmailField.classList.add("is-invalid");
          EmailFeedBackArea.style.display = "block";
          EmailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
        }
        else{
          SubmitBtn.removeAttribute("disabled");
        };
      });
  };
};

//Email Validation End



//Password Show Start

const PasswordField = document.querySelector("#PasswordField");
const ShowPasswordToogle = document.querySelector(".ShowPasswordToogle");

ShowPasswordToogle.addEventListener("click", HandleToggleInput);

function HandleToggleInput(event){
  if (ShowPasswordToogle.textContent === "SHOW"){
    ShowPasswordToogle.textContent = "HIDE";
    PasswordField.setAttribute("type", "text");
  }
  else{
    ShowPasswordToogle.textContent = "SHOW";
    PasswordField.setAttribute("type", "password");
  }
};
//Password Show End


