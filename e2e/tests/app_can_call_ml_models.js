Feature('Image Lab');

// testing if clicking a filter trigger the ML API call
Scenario('applying a ML filter sends an API request', ({ I }) => {
  I.amOnPage('/');

  I.startRecordingTraffic();                          

  I.attachFile('#file-input', '../assets/andrewdick.jpg'); 
  I.click('Remove Background');                                

  I.seeTraffic({                                     
    name: 'remove backgroundi request',
    url: '/ml/remove-background',
  });
});