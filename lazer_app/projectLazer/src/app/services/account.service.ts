import { Injectable } from '@angular/core';
import { SwUpdate } from '@angular/service-worker';

@Injectable({
  providedIn: 'root',
})
export class AccountService {
  username: string | null = null;
  loggedIn: boolean = false;

  async logIn(username: string, password: string) {
    const url = '/lazer/api/login/';
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify({ username: username, password: password }),
      });
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const json = await response.json();
      this.username = json.username;
      this.loggedIn = true;
    } catch (error: any) {
      console.log(error.message);
    }
  }

  async logOut() {
    const url = '/lazer/api/logout/';
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const json = await response.json();
      this.username = null;
      this.loggedIn = false;
    } catch (error: any) {
      console.log(error.message);
    }
  }

  constructor() {}
}
