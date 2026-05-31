Feature('Image Lab');

Scenario('the home page loads', ({ I }) => {  
    I.amOnPage('/');     
    I.see('Image Lab');  
});
