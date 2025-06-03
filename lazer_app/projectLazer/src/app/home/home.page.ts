import { Capacitor } from '@capacitor/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Component, OnInit } from '@angular/core';
import { Device, DeviceInfo } from '@capacitor/device';
import { Geolocation, Position } from '@capacitor/geolocation';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: false,
})
export class HomePage implements OnInit {

  deviceInfo: DeviceInfo | null = null;
  geoPerms: boolean | null = null;

  myImage: string | undefined | null = null;
  position: Position | null = null;

  constructor() {}

  async getCurrentPosition() {
    Geolocation.getCurrentPosition({enableHighAccuracy: true, maximumAge: 30000})
    .then(
      (coordinates) => {
        this.position = coordinates;
        this.geoPerms = true;
      }
    );
  }

  async takePicture() {
    this.getCurrentPosition();

    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.Uri,
      source: CameraSource.Camera,
      webUseInput: true
    });

    this.myImage = image.webPath;
  }

  async submit() {
    this.myImage = null;
    this.position = null;
  }

  requestGeoPerms = () => {
    if ( Capacitor.isNativePlatform() ){
      Geolocation.requestPermissions();
    } else {
      this.getCurrentPosition();
    }
    this.checkPermission();
  }

  checkPermission = async () => {
    if ( Capacitor.isNativePlatform() ){
      try {
        const status = await Geolocation.checkPermissions();
        if (status) {
          this.geoPerms = true;
        }
        this.geoPerms = false;
      } catch(e) {
        console.log(e);
        this.geoPerms = false;
      }
    } else {
      navigator.permissions.query({ name: "geolocation" }).then((result) => {
        if (result.state === "granted") {
          this.geoPerms = true;
        } else if (result.state === "prompt") {
          if (this.deviceInfo !== null && this.deviceInfo.operatingSystem === "ios") {
            this.geoPerms = true;
          } else {
            this.geoPerms = false;
          }
        } else {
          this.geoPerms = false;
        }
      });
    }
  }

  ngOnInit(): void {
    Device.getInfo().then((deviceInfo) => {
      this.deviceInfo = deviceInfo;
      this.checkPermission();
    });
  }

}
