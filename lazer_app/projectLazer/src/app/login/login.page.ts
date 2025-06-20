import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

import { NgForm } from '@angular/forms';

import { OnlineStatusService } from '../services/online.service';
import { UpdateService } from '../services/update.service';
import { AccountService } from '../services/account.service';

interface UserOptions {
  username: string;
  password: string;
}

@Component({
  selector: 'app-login',
  templateUrl: './login.page.html',
  styleUrls: ['./login.page.scss'],
  standalone: false,
})
export class LoginPage implements OnInit {
  login: UserOptions = { username: '', password: '' };
  submitted = false;

  constructor(
    public accountService: AccountService,
    public onlineStatus: OnlineStatusService,
    public updateService: UpdateService,
    private router: Router
  ) {}

  onLogin(form: NgForm) {
    this.submitted = true;

    if (form.valid) {
      this.accountService.logIn(this.login.username, this.login.password);
      this.router.navigate(['home']);
    }
  }

  ngOnInit() {}
}
