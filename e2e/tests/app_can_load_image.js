Feature('Image Lab');

// testing if clicking a filter trigger the API call?
Scenario('applying a filter sends an API request', ({ I }) => {
  I.amOnPage('/');

  I.startRecordingTraffic();                          

  I.attachFile('#file-input', '../assets/andrewdick.jpg'); 
  I.click('Sharpen');                                

  I.seeTraffic({                                     
    name: 'sharpen request',
    url: '/filters/sharpen',
  });
});


