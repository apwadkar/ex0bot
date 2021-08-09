import Ex0botStack from "./Ex0botStack";
import { App } from "@serverless-stack/resources";

export default function main(app: App): void {
  app.setDefaultFunctionProps({
    runtime: "nodejs14.x",
    environment: {
      REDIS_URL: process.env.REDIS_URL || ""
    }
  });

  new Ex0botStack(app, "ex0bot-api-stack");
}
