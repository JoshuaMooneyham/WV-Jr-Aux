console.log('hi')
try {
    console.log('trying')
    let time = document.getElementById('remaining');
    let timeList = time.innerText.split(":");
    let hour = parseInt(timeList[0]);
    let minute = parseInt(timeList[1]);
    let second = parseInt(timeList[2]);
    
    function changeTime() {

        if (minute == 0 && hour > 0) {
            minute = 59
            hour -= 1;
        }
        if (second == 0 && minute > 0) {
            second = 60;
            minute -= 1;
        }
        if (second > 0) {
            second -= 1;
        }
        timeString = (`${hour}`.length > 1 ? `${hour}` : `0${hour}`) + ':' + (`${minute}`.length > 1 ? `${minute}` : `0${minute}`) + ":" + (`${second}`.length > 1 ? `${second}` : `0${second}`);
        // time.innerText = `${hour}:${minute}:${second}`;
        time.innerText = timeString;
    }

    setInterval(changeTime, 1000)
  } catch {
    console.log('TimerError')
  }