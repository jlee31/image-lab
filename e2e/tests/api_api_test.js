Feature('Image Lab');

const fs = require('fs');
const FormData = require('form-data');

// API TEST
Scenario('the blur endpoint returns 200 for an uploaded image', async ({ I }) => {
  const form = new FormData();

  form.append('file', fs.createReadStream('../assets/andrewdick.jpg'));

  await I.sendPostRequest('/filters/blur?radius=5', form, form.getHeaders());

  I.seeResponseCodeIs(200); 

});

// run with npx codeceptjs run --steps 