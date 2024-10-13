// ==UserScript==
// @name         GeoGuessr Team Balancer
// @namespace    http://tampermonkey.net/
// @version      1.0
// @description  Extracts player usernames from the GeoGuessr lobby and sends them to a Python script for team balancing.
// @author       Cosine
// @match        *://www.geoguessr.com/*
// @grant        GM_xmlhttpRequest
// ==/UserScript==

(function() {
    'use strict';

    // Function to extract usernames from the lobby
    function getUsernames() {
        let usernames = [];
        // Adjust the selector based on the actual GeoGuessr lobby HTML structure
        document.querySelectorAll(".player-username-selector").forEach(player => {
            usernames.push(player.innerText.trim());
        });
        return usernames;
    }

    // Function to send usernames to the local Python server
    function sendUsernames(usernames) {
        GM_xmlhttpRequest({
            method: "POST",
            url: "http://localhost:5000/usernames",
            headers: {
                "Content-Type": "application/json"
            },
            data: JSON.stringify({ usernames: usernames }),
            /**
             * Called when the response to the POST request is received.
             * Prints the response text to the console.
             * @param {Object} response - The response object from the POST request.
             */
            onload: function(response) {
                console.log("Usernames sent:", response.responseText);
            }
        });
    }

    // Button to trigger the team balancing
    let balanceTeamsButton = document.createElement("button");
    balanceTeamsButton.innerText = "Balance Teams";
    balanceTeamsButton.style.position = "absolute";
    balanceTeamsButton.style.top = "10px";
    balanceTeamsButton.style.right = "10px";
    balanceTeamsButton.style.zIndex = 1000;
    /**
     * Event handler for the "Balance Teams" button. Sends a list of player
     * usernames in the lobby to the local Python server for team balancing.
     */
    balanceTeamsButton.onclick = function() {
        let usernames = getUsernames();
        sendUsernames(usernames);
    };

    document.body.appendChild(balanceTeamsButton);
})();
