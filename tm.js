// ==UserScript==
// @name         Geoguessr Balance Teams
// @description  Adds a Balance Teams button to the Geoguessr settings menu to balance teams.
// @version      1.0.1
// @author       Sirey
// @license      MIT
// @match        https://www.geoguessr.com/*
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const balanceTeamsEndpoint = "http://localhost:5000/balance-teams"; // URL of your backend endpoint
    let members = [];
    let partyId = ''; // This will be fetched from the API

    // Function to fetch the partyId
    async function fetchPartyId() {
        try {
            const response = await fetch('https://www.geoguessr.com/api/v4/parties/v2');
            const data = await response.json();
            if (data && data.partyId) {
                partyId = data.partyId;
                console.log('Party ID retrieved:', partyId);
                connectWebSocket(); // Connect to WebSocket after fetching partyId
            } else {
                throw new Error('Party ID not found');
            }
        } catch (error) {
            console.error('Failed to fetch Party ID:', error);
        }
    }

    // Function to connect to the WebSocket
    function connectWebSocket() {
        const socket = new WebSocket('wss://api.geoguessr.com/ws');

        socket.onopen = () => {
            console.log('WebSocket connection opened');
            // Subscribe to the party
            socket.send(JSON.stringify({ code: 'Subscribe', topic: 'partyv2:' + partyId }));
        };

        socket.onmessage = ({ data }) => {
            try {
                const received = JSON.parse(data);
                if (received.code === 'PartyMemberListUpdated') {
                    const payload = JSON.parse(received.payload);
                    members = payload.members;
                    console.log('Members updated:', members);
                }
            } catch (e) {
                console.error('Error processing WebSocket message:', e);
            }
        };

        socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        socket.onclose = () => {
            console.log('WebSocket connection closed');
        };
    }

    // Function to send the request to balance teams
    function sendBalanceTeamsRequest() {
        // Ensure members are populated
        if (members.length === 0) {
            alert('No members found. Please ensure you are in a lobby and try again.');
            return;
        }

        // Extract user IDs from members
        const userIds = members.map(member => member.userId);

        fetch(balanceTeamsEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: 'balance_teams', user_ids: userIds })
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Failed to balance teams');
            }
        })
        .then(data => {
            alert('Teams balanced successfully:\n' + JSON.stringify(data, null, 2));
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please check the console for details.');
        });
    }

    // HTML for the "Balance Teams" button
    const balanceTeamsButtonHTML = `
        <div style="margin-top: 10px">
            <button id="balanceTeamsButton" style="background-color: #4CAF50; color: white; border: none; border-radius: 5px; padding: 10px; cursor: pointer;">
                Balance Teams
            </button>
        </div>
    `;

    // Function to add the Balance Teams button to the settings menu
    function addBalanceTeamsButton() {
        const settingsSection = document.querySelector('[class*=settings-modal_section__]');
        if (settingsSection && !document.querySelector('#balanceTeamsButton')) {
            settingsSection.insertAdjacentHTML('beforeend', balanceTeamsButtonHTML);
            document.querySelector('#balanceTeamsButton').addEventListener('click', sendBalanceTeamsRequest);
        }
    }

    // Check for the settings menu and add the Balance Teams button
    const observer = new MutationObserver(() => {
        addBalanceTeamsButton();
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Fetch the partyId and connect to the WebSocket after
    fetchPartyId();
})();
