// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom';

global.clearImmediate = global.clearImmediate || ((t) => clearTimeout(t));
global.setImmediate = global.setImmediate || ((cb, ...args) => setTimeout(cb, 0, ...args));