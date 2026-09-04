const stickman = document.getElementById("stickman");
const stickBody = document.getElementById("stickBody");

const armL = document.getElementById("armL");
const armR = document.getElementById("armR");

const legL = document.getElementById("legL");
const legR = document.getElementById("legR");

const handL = document.getElementById("handL");
const handR = document.getElementById("handR");

const caption = document.getElementById("caption");
const fade = document.getElementById("fade");

const pedestal = document.getElementById("pedestal");
const button = document.getElementById("button");
const question = document.getElementById("question");

const episodeTitle = document.getElementById("episodeTitle");

const startScreen = document.getElementById("startScreen");
const startButton = document.getElementById("startButton");

const endCard = document.getElementById("endCard");
const replay = document.getElementById("replay");

const rotateHint = document.getElementById("rotateHint");

const backgroundMusic =
    document.getElementById("backgroundMusic");

const clickAudio =
    document.getElementById("clickAudio");

const popAudio =
    document.getElementById("popAudio");

const stepAudio =
    document.getElementById("stepAudio");

let audioContext = null;
let masterGain = null;
let musicGain = null;
let musicTimer = null;

let running = false;

function sleep(ms) {
    return new Promise(resolve => {
        setTimeout(resolve, ms);
    });
}

function setCaption(text, duration = 0) {

    caption.textContent = text;

    caption.classList.toggle(
        "show",
        Boolean(text)
    );

    if (duration) {

        setTimeout(() => {

            if (caption.textContent === text) {
                caption.classList.remove("show");
            }

        }, duration);
    }
}

function speak(
    text,
    rate = 1,
    pitch = 1
) {

    if (!("speechSynthesis" in window)) {
        return Promise.resolve();
    }

    return new Promise(resolve => {

        speechSynthesis.cancel();

        const voice =
            new SpeechSynthesisUtterance(text);

        voice.rate = rate;
        voice.pitch = pitch;
        voice.volume = .95;

        let finished = false;

        const done = () => {

            if (finished) return;

            finished = true;
            resolve();
        };

        voice.onend = done;
        voice.onerror = done;

        speechSynthesis.speak(voice);

        setTimeout(
            done,
            Math.max(
                2500,
                text.length * 75
            )
        );
    });
}

function ensureAudio() {

    if (audioContext) {

        if (
            audioContext.state ===
            "suspended"
        ) {
            audioContext.resume();
        }

        return;
    }

    const AudioContext =
        window.AudioContext ||
        window.webkitAudioContext;

    if (!AudioContext) {
        return;
    }

    audioContext = new AudioContext();

    masterGain =
        audioContext.createGain();

    masterGain.gain.value = .45;

    masterGain.connect(
        audioContext.destination
    );

    musicGain =
        audioContext.createGain();

    musicGain.gain.value = .08;

    musicGain.connect(masterGain);

    startMusic();
}

function tone(
    frequency,
    duration = .12,
    type = "sine",
    volume = .1
) {

    if (!audioContext) return;

    const oscillator =
        audioContext.createOscillator();

    const gain =
        audioContext.createGain();

    oscillator.type = type;
    oscillator.frequency.value = frequency;

    gain.gain.setValueAtTime(
        .0001,
        audioContext.currentTime
    );

    gain.gain.exponentialRampToValueAtTime(
        volume,
        audioContext.currentTime + .015
    );

    gain.gain.exponentialRampToValueAtTime(
        .0001,
        audioContext.currentTime + duration
    );

    oscillator.connect(gain);
    gain.connect(masterGain);

    oscillator.start();

    oscillator.stop(
        audioContext.currentTime +
        duration +
        .03
    );
}

function startMusic() {

    if (musicTimer) return;

    const notes = [
        261.63,
        329.63,
        392.00,
        329.63,
        293.66,
        349.23,
        440.00,
        349.23
    ];

    let index = 0;

    musicTimer = setInterval(() => {

        if (!audioContext || !running) {
            return;
        }

        const oscillator =
            audioContext.createOscillator();

        const gain =
            audioContext.createGain();

        oscillator.type = "triangle";

        oscillator.frequency.value =
            notes[index];

        gain.gain.setValueAtTime(
            .0001,
            audioContext.currentTime
        );

        gain.gain.exponentialRampToValueAtTime(
            .055,
            audioContext.currentTime + .04
        );

        gain.gain.exponentialRampToValueAtTime(
            .0001,
            audioContext.currentTime + .65
        );

        oscillator.connect(gain);
        gain.connect(musicGain);

        oscillator.start();

        oscillator.stop(
            audioContext.currentTime + .7
        );

        index =
            (index + 1) % notes.length;

    }, 700);
}

function stopMusic() {

    if (!musicTimer) return;

    clearInterval(musicTimer);

    musicTimer = null;
}

function playElementAudio(element) {

    if (!element.src) {
        return false;
    }

    try {

        element.currentTime = 0;

        const promise = element.play();

        if (promise) {
            promise.catch(() => {});
        }

        return true;

    } catch {
        return false;
    }
}

function playClick() {

    if (!playElementAudio(clickAudio)) {
        tone(
            150,
            .06,
            "square",
            .12
        );
    }
}

function playPop() {

    if (!playElementAudio(popAudio)) {

        tone(
            480,
            .08,
            "triangle",
            .14
        );

        setTimeout(() => {

            tone(
                720,
                .11,
                "sine",
                .12
            );

        }, 65);
    }
}

function playStep() {

    if (!playElementAudio(stepAudio)) {

        tone(
            120,
            .055,
            "triangle",
            .06
        );
    }
}

function resetPose() {

    armL.setAttribute(
        "x2",
        "31"
    );

    armL.setAttribute(
        "y2",
        "81"
    );

    armR.setAttribute(
        "x2",
        "85"
    );

    armR.setAttribute(
        "y2",
        "81"
    );

    legL.setAttribute(
        "x2",
        "39"
    );

    legL.setAttribute(
        "y2",
        "123"
    );

    legR.setAttribute(
        "x2",
        "77"
    );

    legR.setAttribute(
        "y2",
        "123"
    );

    handL.setAttribute(
        "cx",
        "31"
    );

    handL.setAttribute(
        "cy",
        "81"
    );

    handR.setAttribute(
        "cx",
        "85"
    );

    handR.setAttribute(
        "cy",
        "81"
    );
}

function walkPose(step) {

    if (step % 2 === 0) {

        armL.setAttribute(
            "x2",
            "35"
        );

        armL.setAttribute(
            "y2",
            "89"
        );

        armR.setAttribute(
            "x2",
            "82"
        );

        armR.setAttribute(
            "y2",
            "72"
        );

        legL.setAttribute(
            "x2",
            "78"
        );

        legL.setAttribute(
            "y2",
            "123"
        );

        legR.setAttribute(
            "x2",
            "39"
        );

        legR.setAttribute(
            "y2",
            "118"
        );

        handL.setAttribute(
            "cx",
            "35"
        );

        handL.setAttribute(
            "cy",
            "89"
        );

        handR.setAttribute(
            "cx",
            "82"
        );

        handR.setAttribute(
            "cy",
            "72"
        );

    } else {

        armL.setAttribute(
            "x2",
            "35"
        );

        armL.setAttribute(
            "y2",
            "72"
        );

        armR.setAttribute(
            "x2",
            "82"
        );

        armR.setAttribute(
            "y2",
            "89"
        );

        legL.setAttribute(
            "x2",
            "39"
        );

        legL.setAttribute(
            "y2",
            "123"
        );

        legR.setAttribute(
            "x2",
            "78"
        );

        legR.setAttribute(
            "y2",
            "118"
        );

        handL.setAttribute(
            "cx",
            "35"
        );

        handL.setAttribute(
            "cy",
            "72"
        );

        handR.setAttribute(
            "cx",
            "82"
        );

        handR.setAttribute(
            "cy",
            "89"
        );
    }
}

async function walkTo(
    targetPercent,
    duration
) {

    stickman.classList.add("walk");

    const start =
        parseFloat(
            getComputedStyle(
                stickman
            ).left
        );

    const target =
        targetPercent;

    const startTime =
        performance.now();

    let lastStep = -1;

    return new Promise(resolve => {

        function frame(now) {

            const progress =
                Math.min(
                    1,
                    (now - startTime) /
                    duration
                );

            const eased =
                progress < .5
                    ? 2 * progress * progress
                    : 1 -
                      Math.pow(
                          -2 * progress + 2,
                          2
                      ) / 2;

            const value =
                start +
                (target - start) *
                eased;

            stickman.style.left =
                value + "%";

            const step =
                Math.floor(
                    progress * 12
                );

            if (
                step !== lastStep &&
                step % 2 === 0
            ) {

                walkPose(step);
                playStep();

                lastStep = step;
            }

            if (progress < 1) {

                requestAnimationFrame(
                    frame
                );

            } else {

                stickman.classList.remove(
                    "walk"
                );

                resetPose();

                resolve();
            }
        }

        requestAnimationFrame(frame);
    });
}

async function wave() {

    for (let i = 0; i < 4; i++) {

        const extended =
            i % 2 === 1;

        armR.setAttribute(
            "x2",
            extended ? "96" : "105"
        );

        armR.setAttribute(
            "y2",
            extended ? "56" : "45"
        );

        handR.setAttribute(
            "cx",
            extended ? "96" : "105"
        );

        handR.setAttribute(
            "cy",
            extended ? "56" : "45"
        );

        tone(
            extended ? 430 : 500,
            .08,
            "sine",
            .07
        );

        await sleep(230);
    }

    resetPose();
}

async function pointAtButton() {

    armR.setAttribute(
        "x2",
        "90"
    );

    armR.setAttribute(
        "y2",
        "70"
    );

    handR.setAttribute(
        "cx",
        "90"
    );

    handR.setAttribute(
        "cy",
        "70"
    );

    await sleep(700);

    resetPose();
}

async function pressButton() {

    button.style.transform =
        "scale(.72)";

    button.style.boxShadow =
        "0 2px 0 #922222, " +
        "0 0 25px rgba(255,80,80,.8)";

    playClick();

    await sleep(120);

    button.style.transform =
        "scale(1)";
}

async function transition() {

    fade.classList.add("on");

    await sleep(520);

    fade.classList.remove("on");

    await sleep(520);
}

async function requestLandscapeFullscreen() {

    try {

        if (!document.fullscreenElement) {

            await document
                .documentElement
                .requestFullscreen({
                    navigationUI: "hide"
                });
        }

    } catch (error) {

        console.log(
            "Fullscreen unavailable:",
            error
        );
    }

    try {

        if (
            screen.orientation &&
            screen.orientation.lock
        ) {

            await screen.orientation.lock(
                "landscape"
            );
        }

    } catch (error) {

        console.log(
            "Landscape lock unavailable:",
            error
        );
    }
}

function updateRotateHint() {

    const portrait =
        window.innerHeight >
        window.innerWidth;

    if (
        portrait &&
        startScreen.style.display ===
            "none"
    ) {

        rotateHint.classList.add(
            "active"
        );

    } else {

        rotateHint.classList.remove(
            "active"
        );
    }
}

window.addEventListener(
    "resize",
    updateRotateHint
);

window.addEventListener(
    "orientationchange",
    updateRotateHint
);

async function playEpisode() {

    if (running) return;

    running = true;

    ensureAudio();

    episodeTitle.style.opacity = "1";

    stickman.style.left = "-14%";

    pedestal.style.opacity = "0";

    question.classList.remove(
        "questionShow"
    );

    button.style.background = "#e74747";
    button.style.borderColor = "#b92c2c";

    button.style.boxShadow =
        "0 5px 0 #922222, " +
        "0 0 18px rgba(255,80,80,.45)";

    resetPose();

    setCaption("");

    await sleep(900);

    setCaption(
        "Hey. Welcome back."
    );

    await speak(
        "Hey. Welcome back."
    );

    await sleep(450);

    setCaption(
        "I was just taking a walk..."
    );

    await speak(
        "I was just taking a walk.",
        .95
    );

    await walkTo(
        27,
        2500
    );

    await sleep(500);

    setCaption(
        "Then I saw something."
    );

    await speak(
        "Then I saw something."
    );

    pedestal.style.opacity = "1";

    question.classList.add(
        "questionShow"
    );

    playPop();

    await sleep(800);

    setCaption(
        "A button."
    );

    await speak(
        "A button.",
        .9
    );

    await sleep(600);

    question.classList.remove(
        "questionShow"
    );

    setCaption(
        "And there was only one thing to do."
    );

    await speak(
        "And there was only one thing to do.",
        .92
    );

    await walkTo(
        49,
        2200
    );

    await sleep(450);

    await pointAtButton();

    setCaption(
        "Figure out what it does."
    );

    await speak(
        "Figure out what it does.",
        .92
    );

    await sleep(800);

    setCaption(
        "Probably nothing."
    );

    await speak(
        "Probably nothing.",
        .8,
        .9
    );

    await sleep(600);

    setCaption(
        "Right?"
    );

    await speak(
        "Right?",
        .72,
        .85
    );

    await sleep(900);

    setCaption(
        "Okay. I'm pressing it."
    );

    await speak(
        "Okay. I'm pressing it."
    );

    await pressButton();

    await sleep(350);

    const sky =
        document.getElementById(
            "sky"
        );

    const ground =
        document.getElementById(
            "ground"
        );

    const road =
        document.getElementById(
            "road"
        );

    sky.style.transition =
        "filter 1.2s ease";

    ground.style.transition =
        "filter 1.2s ease";

    road.style.transition =
        "filter 1.2s ease";

    sky.style.filter =
        "hue-rotate(35deg) saturate(1.25)";

    ground.style.filter =
        "hue-rotate(80deg) saturate(1.2)";

    road.style.filter =
        "brightness(.82)";

    tone(
        300,
        .25,
        "sine",
        .12
    );

    await sleep(500);

    tone(
        450,
        .3,
        "triangle",
        .1
    );

    await sleep(700);

    sky.style.filter = "";
    ground.style.filter = "";
    road.style.filter = "";

    setCaption(
        "...Nothing happened."
    );

    await speak(
        "Nothing happened.",
        .9,
        .95
    );

    await sleep(1000);

    button.style.background =
        "#45c96b";

    button.style.borderColor =
        "#2e9449";

    button.style.boxShadow =
        "0 5px 0 #217037, " +
        "0 0 25px rgba(70,255,120,.7)";

    playPop();

    await sleep(700);

    setCaption(
        "Wait."
    );

    await speak(
        "Wait.",
        .75,
        1.05
    );

    await sleep(450);

    setCaption(
        "It changed."
    );

    await speak(
        "It changed.",
        .88,
        1.05
    );

    await sleep(600);

    setCaption(
        "That means..."
    );

    await speak(
        "That means...",
        .85
    );

    await sleep(700);

    setCaption(
        "I should probably press it again."
    );

    await speak(
        "I should probably press it again."
    );

    await sleep(450);

    await pressButton();

    await sleep(700);

    tone(
        180,
        .25,
        "sawtooth",
        .08
    );

    await sleep(180);

    tone(
        120,
        .4,
        "sawtooth",
        .06
    );

    await sleep(800);

    setCaption(
        "Yeah."
    );

    await speak(
        "Yeah.",
        .75,
        .95
    );

    await sleep(550);

    setCaption(
        "Definitely shouldn't have done that."
    );

    await speak(
        "Definitely shouldn't have done that.",
        .88,
        .95
    );

    await sleep(900);

    await walkTo(
        75,
        3000
    );

    await sleep(400);

    setCaption(
        "But at least I learned something."
    );

    await speak(
        "But at least I learned something.",
        .9
    );

    await sleep(500);

    setCaption(
        "Never trust a mysterious button."
    );

    await speak(
        "Never trust a mysterious button.",
        .9
    );

    await sleep(700);

    await wave();

    setCaption(
        "See you in Episode 3."
    );

    await speak(
        "See you in Episode 3."
    );

    await sleep(1200);

    episodeTitle.style.opacity = "0";

    setCaption("");

    endCard.style.display = "flex";

    running = false;
}

async function startEpisode() {

    startScreen.style.display = "none";

    ensureAudio();

    await requestLandscapeFullscreen();

    updateRotateHint();

    await sleep(300);

    playEpisode();
}

startButton.addEventListener(
    "click",
    async () => {

        startButton.disabled = true;

        await startEpisode();

        startButton.disabled = false;
    }
);

replay.addEventListener(
    "click",
    async () => {

        endCard.style.display = "none";

        await sleep(300);

        playEpisode();
    }
);

document.addEventListener(
    "fullscreenchange",
    updateRotateHint
);

document.addEventListener(
    "visibilitychange",
    () => {

        if (
            document.hidden &&
            "speechSynthesis" in window
        ) {

            speechSynthesis.cancel();
        }
    }
);
