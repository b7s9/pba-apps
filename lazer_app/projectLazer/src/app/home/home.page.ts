import { Capacitor } from '@capacitor/core';
import { Camera, CameraResultType, CameraSource } from '@capacitor/camera';
import { Component, OnInit } from '@angular/core';
import { Device, DeviceInfo } from '@capacitor/device';
import { Geolocation, Position } from '@capacitor/geolocation';
import { Network } from '@capacitor/network';


@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: false,
})
export class HomePage implements OnInit {

  online: boolean | null = null;
  deviceInfo: DeviceInfo | null = null;
  geoPerms: boolean | null = null;

  violationImage: string | undefined | null = null;
  violationPosition: Position | null = null;
  violationTime: Date | null = null;

  constructor() {}

  async getCurrentPosition() {
    Geolocation.getCurrentPosition({enableHighAccuracy: true, maximumAge: 30000})
    .then(
      (coordinates) => {
        this.violationPosition = coordinates;
        this.geoPerms = true;
      }
    );
  }

  async takePicture() {
    this.getCurrentPosition();

    const image = await Camera.getPhoto({
      quality: 90,
      allowEditing: false,
      resultType: CameraResultType.DataUrl,
      source: CameraSource.Camera,
      webUseInput: true
    });

    this.violationImage = image.dataUrl;
    this.violationTime = new Date();
  }

  async submit() {

    function submitData (lat: number, long: number, dt: Date, img: string): Promise<any> {
      return new Promise((resolve, reject) => {
        let request = new XMLHttpRequest();
        request.addEventListener("readystatechange", () => {
          if (request.readyState === 4 && request.status === 200) {
            let data = JSON.parse(request.responseText);
            resolve(data);
          } else if (request.readyState === 4) {
            reject("error getting resources");
          }
        });

        let formData = new FormData();
        formData.append("latitude", JSON.stringify(lat));
        formData.append("longitude", JSON.stringify(long));
        formData.append("datetime", dt.toISOString());
        formData.append("image", img);

        request.open("POST", "https://lazer.ngrok.io/lazer/submit/");
        request.send(formData);
      });
    }

    if (this.violationImage !== null && this.violationTime !== null && this.violationPosition !== null) {
      await submitData(
        this.violationPosition!.coords!.latitude,
        this.violationPosition!.coords!.longitude,
        this.violationTime!,
        this.violationImage!
      )
      .then((data: any) => {
        this.violationPosition = null;
        this.violationTime = null;
        this.violationImage = null;
      })
      .catch((err: any) => {
        console.log(err);
      });
    }

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
      Network.getStatus().then((connectionStatus) => {
        this.online = connectionStatus.connected;
      });
      Network.addListener('networkStatusChange', connectionStatus => {
        this.online = connectionStatus.connected;
      });
      this.checkPermission();
    });
  }

}
