import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage-angular';

@Injectable({
  providedIn: 'root',
})
export class AccountService {
  username: string | null = null;
  loggedIn: boolean = false;

  async checkLoggedIn() {
    const url = '/lazer/api/check-login/';
    try {
      const response = await fetch(url, {
        method: 'GET',
      });
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const json = await response.json();
      this.username = json.username;
      this.loggedIn = true;
      await this.storage.set('loggedIn', this.username);
    } catch (error: any) {
      console.log(error.message);
      await this.storage.set('loggedIn', null);
    }
  }

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
      await this.storage.set('loggedIn', this.username);
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
      await this.storage.set('loggedIn', null);
    } catch (error: any) {
      console.log(error.message);
    }
  }

  constructor(private storage: Storage) {}
  ngOnInit(): void {
    this.storage.get('loggedIn').then((username) => {
      if (username) {
        this.loggedIn = true;
        this.username = username;
      } else {
        this.loggedIn = false;
        this.username = null;
      }
    });
  }
}
