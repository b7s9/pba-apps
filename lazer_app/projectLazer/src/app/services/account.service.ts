import { Injectable } from '@angular/core';
import { Storage } from '@ionic/storage-angular';
import { ToastController } from '@ionic/angular';

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
      await this.presentSuccess(json);
    } catch (error: any) {
      console.log(error);
      if (error.message) {
        await this.presentError(error.message);
      }
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

  async presentError(message: string) {
    const toast = await this.toastController.create({
      message: 'Invalid Auth: ' + message,
      duration: 1000,
      position: 'top',
      icon: 'alert',
    });
    toast.present();
  }

  async presentSuccess(data: any) {
    const toast = await this.toastController.create({
      message: 'Success! Welcome, ' + data.username,
      duration: 1000,
      position: 'top',
      icon: 'check',
    });
    toast.present();
  }

  constructor(
    private storage: Storage,
    private toastController: ToastController
  ) {}
}
