import { Pipe, PipeTransform } from '@angular/core';
import { Directory, Filesystem } from '@capacitor/filesystem';

@Pipe({
  name: 'renderImage',
  standalone: true,
})
export class RenderImagePipe implements PipeTransform {
  transform(filename: string): any {
    return Filesystem.readFile({
      path: filename,
      directory: Directory.External,
    }).then((readFile) => {
      return `data:image/jpeg;base64,${readFile.data}`;
    });
  }
}
