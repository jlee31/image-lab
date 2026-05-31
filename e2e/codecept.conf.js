// CodeceptJS configuration.
// CodeceptJS is the test framework; it drives a real browser through Playwright.
exports.config = {
  // Where the test files live (any .js file in tests/).
  tests: './tests/**/*.js',

  // The browser engine + the base URL the tests open.
  helpers: {
    Playwright: {
      url: 'http://localhost:8000', // the FastAPI server (start it before running)
      show: false,                  // run headless; set true to watch the browser
      browser: 'chromium',
    },
    // REST drives the API directly over HTTP (no browser). Gives us I.sendPostRequest.
    REST: {
      endpoint: 'http://localhost:8000',
    },
    // JSONResponse adds the assertions about the last REST response,
    // e.g. I.seeResponseCodeIs / I.seeResponseContainsKeys.
    JSONResponse: {},
  },

  // Where screenshots/logs go when a test fails.
  output: './output',

  name: 'image-lab-e2e',
};
