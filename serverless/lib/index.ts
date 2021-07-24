import Ex0botStack from "./Ex0botStack";
import { App } from "@serverless-stack/resources";

export default function main(app: App): void {
  // Set default runtime for all functions
  app.setDefaultFunctionProps({
    runtime: "nodejs14.x"
  });

  new Ex0botStack(app, "ex0bot-api-stack");

  // Add more stacks
}
