let lightMode = true;
let recorder = null;
let recording = false;
let voiceOption = "default";
const botRepeatButtonIDToIndexMap = {};
const userRepeatButtonIDToRecordingMap = {};
const baseUrl = window.location.origin;
const responses = [];

async function showBotLoadingAnimation() {
  await sleep(500);
  $(".loading-animation")[1].style.display = "inline-block";
}

async function hideBotLoadingAnimation() {
  $(".loading-animation")[1].style.display = "none";
}

async function showUserLoadingAnimation() {
  await sleep(100);
  $(".loading-animation")[0].style.display = "flex";
}

async function hideUserLoadingAnimation() {
  $(".loading-animation")[0].style.display = "none";
}

async function sendWelcomeMessage() {
  await sleep(1000);
  const welcomeMessage = "Hello there! I'm Mai, one of Tai's trusted friends, and I'm here to make your dream home search a delightful experience. How can I do to assist you today?";
  const response = await getTextToSpeech(welcomeMessage);
  responses.push(response);

  const repeatButtonID = getRandomID();
  botRepeatButtonIDToIndexMap[repeatButtonID] = responses.length - 1;
  await hideBotLoadingAnimation();
  // Append the random message to the message list
  $("#message-list").append(
     `
      <div class='message-line'>
        <div class='message-box${!lightMode ? " dark" : ""}'>${response.messageText}</div>
        <button id='${repeatButtonID}' class='btn volume repeat-button' onclick='playResponseAudio("data:audio/wav;base64," + responses[botRepeatButtonIDToIndexMap[this.id]].messageSpeech);console.log(this.id)'><i class='fa fa-volume-up'></i></button>
      </div>
     `
  );
  playResponseAudio("data:audio/wav;base64," + response.messageSpeech);
  scrollToBottom();




}

// Add this function to create the table and collect user inputs
async function processRequirementTable() {
  await sleep(1000);
  const formalMessage = "Absolutely! I am happy to assist you with that. As soon as you provide the necessary details, I will begin searching for the most suitable homes for you.";
  const response = await getTextToSpeech(formalMessage);
  responses.push(response);

  const repeatButtonID = getRandomID();
  botRepeatButtonIDToIndexMap[repeatButtonID] = responses.length - 1;
  await hideBotLoadingAnimation();
  // Append the random message to the message list
  $("#message-list").append(
     `
      <div class='message-line'>
        <div class='message-box${!lightMode ? " dark" : ""}'>${response.messageText}</div>
        <button id='${repeatButtonID}' class='btn volume repeat-button' onclick='playResponseAudio("data:audio/wav;base64," + responses[botRepeatButtonIDToIndexMap[this.id]].messageSpeech);console.log(this.id)'><i class='fa fa-volume-up'></i></button>
      </div>
     `
  );
  playResponseAudio("data:audio/wav;base64," + response.messageSpeech);
  scrollToBottom();

  $("#message-list").append(
    `<div class='message-line'>
        <div class='message-box'>
            <table id='requirements-table' class='requirements-table'>
                <tr>
                  <th>Questions</th>
                  <th>Input</th>
                </tr>
                <tr>
                  <td>Location</td>
                  <td><input type='text' id='location' /></td>
                </tr>
                <tr>
                  <td>Building Type</td>
                  <td>
                    <select id='building_type'>
                      <option value='Apartment'>Apartment</option>
                      <option value='House'>House</option>
                      <option value='Townhouse'>Townhouse</option>
                    </select>
                  </td>
                </tr>
                <tr>
                  <td>Bed</td>
                  <td><input type='number' id='beds' /></td>
                </tr>
                <tr>
                  <td>Bath</td>
                  <td><input type='number' id='baths' /></td>
                </tr>
                <tr>
                  <td>Min Price</td>
                  <td><input type='number' id='min_price' /></td>
                </tr>
                <tr>
                  <td>Max Price</td>
                  <td><input type='number' id='max_price' /></td>
                </tr>
                <tr>
                  <td>Special Requirement</td>
                  <td><input type='text' id='special_requirement' /></td>
                </tr>
                <tr>
                  <td colspan='2'>
                    <button id='submit-requirements' class='btn'>Submit</button>
                  </td>
                </tr>
            </table>
        </div>
    </div>
  `);

  // Add event listeners to collect user inputs and submit the form
  $("#submit-requirements").click(async function () {
    const location = $("#location").val();
    const buildingType = $("#building_type").val();
    const beds = $("#beds").val();
    const baths = $("#baths").val();
    const minPrice = $("#min_price").val();
    const maxPrice = $("#max_price").val();
    const specialRequirement = $("#special_requirement").val();

    // Validation function to check if inputs are not empty
    function validateInputs(inputs) {
      for (const input of inputs) {
        if (input.trim() === "") {
          return false;
        }
      }
      return true;
    }

    // Check if inputs are not empty before submitting the form
    if (validateInputs([location, buildingType, beds, baths, minPrice, maxPrice, specialRequirement])) {
      try {
        // After processing the user's requirements, clear the input fields
        $("#requirements-table input, #requirements-table select").val("");

        // Remove the table and the parent container (chat box) after submitting the requirements
        $("#requirements-table").closest('.message-line').remove();

        // Replace with a new message text
        await sleep(1000);
        const formalMessage = "Thank you for sharing your information. Let me analyze your requirements using Realtor.ca and Google search.";
        const thankYouMessage = await getTextToSpeech(formalMessage);
        responses.push(thankYouMessage);

        const repeatButtonID = getRandomID();
        botRepeatButtonIDToIndexMap[repeatButtonID] = responses.length - 1;
        await hideBotLoadingAnimation();
        // Append the random message to the message list
        $("#message-list").append(
           `
            <div class='message-line'>
              <div class='message-box${!lightMode ? " dark" : ""}'>${thankYouMessage.messageText}</div>
              <button id='${repeatButtonID}' class='btn volume repeat-button' onclick='playResponseAudio("data:audio/wav;base64," + responses[botRepeatButtonIDToIndexMap[this.id]].messageSpeech);console.log(this.id)'><i class='fa fa-volume-up'></i></button>
            </div>
           `
        );
        playResponseAudio("data:audio/wav;base64," + thankYouMessage.messageSpeech);

        await showBotLoadingAnimation();
        scrollToBottom();

        let requirement = await fetch(baseUrl + "/process-requirement", {
          method: "POST",
          headers: { Accept: "application/json", "Content-Type": "application/json" },
          body: JSON.stringify({
            location: location,
            buildingType: buildingType,
            beds: beds,
            baths: baths,
            minPrice: minPrice,
            maxPrice: maxPrice,
            specialRequirement: specialRequirement,
          }),
        });
        requirement = await requirement.json();
        console.log(requirement);

        let openaiResponse = await fetch(baseUrl + "/process-openai-review", {
          method: "POST",
          headers: { Accept: "application/json", "Content-Type": "application/json" },
          body: JSON.stringify({
            specialRequirement: specialRequirement,
            listing: requirement.listing,
            listingString: requirement.listingString,
          }),
        });
        openaiResponse = await openaiResponse.json();
        console.log(openaiResponse);

        let response = await fetch(baseUrl + "/process-google-review", {
          method: "POST",
          headers: { Accept: "application/json", "Content-Type": "application/json" },
          body: JSON.stringify({
            location: location,
            openaiReviews: openaiResponse.openaiReviews,
          }),
        });
        response = await response.json();
        console.log(response);

        await showImageAndTable(response.property0Photo, {
          Score: response.property0Score,
          OpenAIReview: response.property0Reason,
          GoogleSearch: response.property0GoogleSearch,
          AddressText: response.property0AddressText,
          Price: response.property0Price,
          Type: response.property0Type,
          Bedrooms: response.property0Bedrooms,
          Bathrooms: response.property0Bathrooms,
          ParkingType: response.property0ParkingType,
          ParkingSpaceTotal: response?.property0ParkingSpaceTotal || "0",
          Ammenities: response.property0Ammenities,
          AmmenitiesNearBy: response?.property0AmmenitiesNearBy || "None",
          RelativeDetailsURL: response?.property0RelativeDetailsURL || "None"
        });
        await sleep(1000);
        await showImageAndTable(response.property1Photo, {
          Score: response.property1Score,
          OpenAIReview: response.property1Reason,
          GoogleSearch: response.property1GoogleSearch,
          AddressText: response.property1AddressText,
          Price: response.property1Price,
          Type: response.property1Type,
          Bedrooms: response.property1Bedrooms,
          Bathrooms: response.property1Bathrooms,
          ParkingType: response.property1ParkingType,
          ParkingSpaceTotal: response?.property1ParkingSpaceTotal || "0",
          Ammenities: response.property1Ammenities,
          AmmenitiesNearBy: response?.property1AmmenitiesNearBy || "None",
          RelativeDetailsURL: response?.property1RelativeDetailsURL || "None"
        });
        /*
        await sleep(1000);
        await showImageAndTable(response.property2Photo, {
          Score: response.property2Score,
          OpenAIReview: response.property2Reason,
          GoogleSearch: response.property2GoogleSearch,
          AddressText: response.property2AddressText,
          Price: response.property2Price,
          Type: response.property2Type,
          Bedrooms: response.property2Bedrooms,
          Bathrooms: response.property2Bathrooms,
          ParkingType: response.property2ParkingType,
          ParkingSpaceTotal: response?.property2ParkingSpaceTotal || "0",
          Ammenities: response.property2Ammenities,
          AmmenitiesNearBy: response?.property2AmmenitiesNearBy || "None",
          RelativeDetailsURL: response?.property2RelativeDetailsURL || "None"
        });
        */
        await hideBotLoadingAnimation();
        return response;
      } catch (error) {
        console.error("Error while fetching data:", error);
      }
    } else {
      alert("Please fill in all the fields before submitting the form.");
    }
  });
}

async function showImageAndTable(imageUrl, propertyData) {
  const tableHtml = createPropertyInfoTable(propertyData);
  const contentHtml = `
    <div class="property-info">
      <img src="${imageUrl}" alt="Property Image" class="image-responsive"/>
      ${tableHtml}
    </div>
  `;

  $("#message-list").append(`
    <div class='message-line'>
      <div class='message-box${!lightMode ? " dark" : ""}'>
        ${contentHtml}
      </div>
    </div>
  `);
  scrollToBottom();
}

function containsKeyword(message) {
  const keywords = ["home", "house", "houses", "Townhouse", "Apartment", "listing", "looking for", "property"];
  return keywords.some(keyword => message.toLowerCase().includes(keyword.toLowerCase()));
}

const createPropertyInfoTable = (data) => {
  const tableHtml = `
    <table class='table-borderless'>
      <tr><td>Score: </td><td>${data.Score}</td></tr>
      <tr><td>Open AI Opinion: </td><td>${data.OpenAIReview}</td></tr>
      <tr><td>Google Search Result: </td><td>${data.GoogleSearch}</td></tr>
      <tr><td>Address: </td><td>${data.AddressText}</td></tr>
      <tr><td>Price: </td><td>${data.Price}</td></tr>
      <tr><td>Type: </td><td>${data.Type}</td></tr>
      <tr><td>Bedrooms: </td><td>${data.Bedrooms}</td></tr>
      <tr><td>Bathrooms: </td><td>${data.Bathrooms}</td></tr>
      <tr><td>Parking Type: </td><td>${data.ParkingType}</td></tr>
      <tr><td>Parking Space Total: </td><td>${data.ParkingSpaceTotal}</td></tr>
      <tr><td>Amenities: </td><td>${data.Ammenities}</td></tr>
      <tr><td>Amenities Nearby: </td><td>${data.AmmenitiesNearBy}</td></tr>
      <tr><td>Relative Details URL: </td><td>${data.RelativeDetailsURL}</td></tr>
    </table>
  `;
  return tableHtml;
};

const getSpeechToText = async (userRecording) => {
  let response = await fetch(baseUrl + "/speech-to-text", {
    method: "POST",
    body: userRecording.audioBlob,
  });
  console.log(response);
  response = await response.json();
  console.log(response);
  return response.text;
};

const getTextToSpeech = async (userMessage) => {
  let response = await fetch(baseUrl + "/text-to-speech", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ userMessage: userMessage, voice: voiceOption }),
  });
  response = await response.json();
  console.log(response);
  return response;
};

const processUserMessage = async (userMessage) => {
  let response = await fetch(baseUrl + "/process-message", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ userMessage: userMessage, voice: voiceOption }),
  });
  response = await response.json();
  console.log(response);
  return response;
};

const cleanTextInput = (value) => {
  return value
    .trim() // remove starting and ending spaces
    .replace(/[\n\t]/g, "") // remove newlines and tabs
    .replace(/<[^>]*>/g, "") // remove HTML tags
    .replace(/[<>&;]/g, ""); // sanitize inputs
};

const recordAudio = () => {
  return new Promise(async (resolve) => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const audioChunks = [];

    mediaRecorder.addEventListener("dataavailable", (event) => {
      audioChunks.push(event.data);
    });

    const start = () => mediaRecorder.start();

    const stop = () =>
      new Promise((resolve) => {
        mediaRecorder.addEventListener("stop", () => {
          const audioBlob = new Blob(audioChunks, { type: "audio/mpeg" });
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          const play = () => audio.play();
          resolve({ audioBlob, audioUrl, play });
        });

        mediaRecorder.stop();
      });

    resolve({ start, stop });
  });
};

const sleep = (time) => new Promise((resolve) => setTimeout(resolve, time));

const toggleRecording = async () => {
  if (!recording) {
    recorder = await recordAudio();
    recording = true;
    recorder.start();
  } else {
    const audio = await recorder.stop();
    sleep(1000);
    return audio;
  }
};

const playResponseAudio = (function () {
  const df = document.createDocumentFragment();
  return function Sound(src) {
    const snd = new Audio(src);
    df.appendChild(snd); // keep in fragment until finished playing
    snd.addEventListener("ended", function () {
      df.removeChild(snd);
    });
    snd.play();
    return snd;
  };
})();

const getRandomID = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2);
};

const scrollToBottom = () => {
  // Scroll the chat window to the bottom
  $("#chat-window").animate({
    scrollTop: $("#chat-window")[0].scrollHeight,
  });
};

const populateUserMessage = (userMessage, userRecording) => {
  // Clear the input field
  $("#message-input").val("");

  // Append the user's message to the message list
  if (userRecording) {
    const userRepeatButtonID = getRandomID();
    userRepeatButtonIDToRecordingMap[userRepeatButtonID] = userRecording;
    hideUserLoadingAnimation();
    $("#message-list").append(
      `<div class='message-line my-text'><div class='message-box my-text${
        !lightMode ? " dark" : ""
      }'><div class='me'>${userMessage}</div></div>
            <button id='${userRepeatButtonID}' class='btn volume repeat-button' onclick='userRepeatButtonIDToRecordingMap[this.id].play()'><i class='fa fa-volume-up'></i></button>
            </div>`
    );
  } else {
    $("#message-list").append(
      `<div class='message-line my-text'><div class='message-box my-text${
        !lightMode ? " dark" : ""
      }'><div class='me'>${userMessage}</div></div></div>`
    );
  }
  scrollToBottom();
};

const populateBotResponse = async (userMessage) => {
   if (containsKeyword(userMessage)) {
     await showBotLoadingAnimation();
     await sleep(2100);
     await hideBotLoadingAnimation();

     const response = await processRequirementTable();
     responses.push(response);

     const repeatButtonID = getRandomID();
     botRepeatButtonIDToIndexMap[repeatButtonID] = responses.length - 1;

     scrollToBottom();
   } else {
     await showBotLoadingAnimation();
     const response = await processUserMessage(userMessage);
     responses.push(response);

     const repeatButtonID = getRandomID();
     botRepeatButtonIDToIndexMap[repeatButtonID] = responses.length - 1;
     await hideBotLoadingAnimation();
     // Append the random message to the message list
     $("#message-list").append(
         `
          <div class='message-line'>
            <div class='message-box${!lightMode ? " dark" : ""}'>${response.openaiResponseText}</div>
            <button id='${repeatButtonID}' class='btn volume repeat-button' onclick='playResponseAudio("data:audio/wav;base64," + responses[botRepeatButtonIDToIndexMap[this.id]].openaiResponseSpeech);console.log(this.id)'><i class='fa fa-volume-up'></i></button>
          </div>
         `
     );
     playResponseAudio("data:audio/wav;base64," + response.openaiResponseSpeech);
     scrollToBottom();
   }
};

$(document).ready(function () {
  // Call the sendWelcomeMessage function to send the welcome message
  sendWelcomeMessage();

  // Listen for the "Enter" key being pressed in the input field
  $("#message-input").keyup(function (event) {
    let inputVal = cleanTextInput($("#message-input").val());

    if (event.keyCode === 13 && inputVal != "") {
      const message = inputVal;

      populateUserMessage(message, null);
      populateBotResponse(message);
    }

    inputVal = $("#message-input").val();

    if (inputVal == "" || inputVal == null) {
      $("#send-button")
        .removeClass("send")
        .addClass("microphone")
        .html("<i class='fa fa-microphone'></i>");
    } else {
      $("#send-button")
        .removeClass("microphone")
        .addClass("send")
        .html("<i class='fa fa-paper-plane'></i>");
    }
  });

  // When the user clicks the "Send" button
  $("#send-button").click(async function () {
    if ($("#send-button").hasClass("microphone") && !recording) {
      toggleRecording();
      $(".fa-microphone").css("color", "#f44336");
      console.log("start recording");
      recording = true;
    } else if (recording) {
      toggleRecording().then(async (userRecording) => {
        console.log("stop recording");
        await showUserLoadingAnimation();
        const userMessage = await getSpeechToText(userRecording);
        populateUserMessage(userMessage, userRecording);
        populateBotResponse(userMessage);
      });
      $(".fa-microphone").css("color", "#125ee5");
      recording = false;
    } else {
      // Get the message the user typed in
      const message = cleanTextInput($("#message-input").val());

      populateUserMessage(message, null);
      populateBotResponse(message);

      $("#send-button")
        .removeClass("send")
        .addClass("microphone")
        .html("<i class='fa fa-microphone'></i>");
    }
  });

  $("#voice-options").change(function () {
    voiceOption = $(this).val();
    console.log(voiceOption);
  });
});
